"""악기 분리 — 밴드 음원에서 베이스 / 드럼 / 나머지(기타·건반) 소리를 떼어 낸다.

2021 Music Demixing Challenge 에서 좋은 성적을 낸 KUIELab 의 MDX-Net 모델(ONNX)을 쓴다.
모델은 UVR(Ultimate Vocal Remover) 프로젝트가 GitHub 에 올려 둔 파일을 처음 쓸 때 내려받는다.

모델 입력은 스테레오 스펙트로그램 조각(실수·허수 × 좌·우 = 4채널, 주파수 dim_f × 시간 dim_t)이고
출력은 같은 모양의 "그 악기만 남은" 스펙트로그램이다. 조각 경계가 튀지 않도록 앞뒤를
n_fft/2 만큼 겹쳐 잘라 넣고 가운데만 이어 붙인다.
"""

from __future__ import annotations

import urllib.request
from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

MODEL_URL = "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/{}"
CACHE = Path.home() / ".cache" / "music2score"
SAMPLE_RATE = 44100
HOP = 1024


@dataclass(frozen=True)
class MdxModel:
    file: str
    n_fft: int
    dim_f: int = 2048
    dim_t: int = 512
    compensate: float = 1.035  # 모델 출력이 살짝 작게 나오는 것을 보정


STEMS = {
    "bass": MdxModel("kuielab_a_bass.onnx", n_fft=16384),
    "drums": MdxModel("kuielab_a_drums.onnx", n_fft=4096),
    "other": MdxModel("kuielab_a_other.onnx", n_fft=8192),  # 기타·건반 등 나머지 악기
}


def separate(path: str | Path, stem: str, out_path: str | Path | None = None) -> Path:
    """path 음원에서 stem("bass" | "drums" | "other") 소리만 뽑아 WAV 로 저장하고 경로를 돌려준다."""
    if stem not in STEMS:
        raise ValueError(f"알 수 없는 악기: {stem} (가능: {', '.join(STEMS)})")
    try:
        import onnxruntime as ort
    except ImportError as e:
        raise RuntimeError("악기 분리(--stem)에는 onnxruntime 이 필요합니다: pip install onnxruntime") from e
    import soundfile as sf

    model = STEMS[stem]
    session = ort.InferenceSession(str(_download(model.file)), providers=["CPUExecutionProvider"])

    mix, _ = librosa.load(str(path), sr=SAMPLE_RATE, mono=False)
    if mix.ndim == 1:
        mix = np.stack([mix, mix])
    out = _demix(mix, session, model) * model.compensate

    path = Path(path)
    out_path = Path(out_path) if out_path else path.with_name(f"{path.stem}.{stem}.wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_path, out.T, SAMPLE_RATE)
    return out_path


def _download(name: str) -> Path:
    target = CACHE / name
    if not target.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        print(f"  악기 분리 모델 내려받는 중: {name} (약 30MB, 처음 한 번만)", flush=True)
        tmp = target.with_suffix(".part")
        urllib.request.urlretrieve(MODEL_URL.format(name), tmp)
        tmp.rename(target)
    return target


def _demix(mix: np.ndarray, session, model: MdxModel, batch: int = 4) -> np.ndarray:
    chunk = HOP * (model.dim_t - 1)
    trim = model.n_fft // 2
    gen = chunk - 2 * trim  # 조각마다 실제로 쓰는 가운데 길이
    n = mix.shape[1]
    pad = gen - n % gen
    padded = np.concatenate([np.zeros((2, trim)), mix, np.zeros((2, pad + trim))], axis=1)

    starts = range(0, n + pad, gen)
    pieces = []
    for i in range(0, len(starts), batch):
        waves = np.stack([padded[:, s : s + chunk] for s in list(starts)[i : i + batch]])
        spec = _stft(waves, model)
        est = session.run(None, {"input": spec.astype(np.float32)})[0]
        pieces.append(_istft(est, model, chunk)[:, :, trim:-trim])
    out = np.concatenate(pieces).transpose(1, 0, 2).reshape(2, -1)
    return out[:, :n]


def _stft(waves: np.ndarray, model: MdxModel) -> np.ndarray:
    """(조각, 2, 샘플) → (조각, 4, dim_f, dim_t). 채널 순서: 왼쪽 실수·허수, 오른쪽 실수·허수."""
    spec = librosa.stft(waves, n_fft=model.n_fft, hop_length=HOP, window="hann", center=True, pad_mode="reflect")
    spec = spec[:, :, : model.dim_f]  # (조각, 2, dim_f, dim_t)
    stacked = np.stack([spec.real, spec.imag], axis=2)  # (조각, 2, 2, dim_f, dim_t)
    return stacked.reshape(len(waves), 4, model.dim_f, -1)


def _istft(spec: np.ndarray, model: MdxModel, length: int) -> np.ndarray:
    n_bins = model.n_fft // 2 + 1
    spec = spec.reshape(len(spec), 2, 2, model.dim_f, -1)
    full = np.zeros((len(spec), 2, n_bins, spec.shape[-1]), dtype=np.complex64)
    full[:, :, : model.dim_f] = spec[:, :, 0] + 1j * spec[:, :, 1]
    return librosa.istft(full, hop_length=HOP, window="hann", center=True, length=length)
