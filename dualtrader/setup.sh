#!/bin/bash
# ──────────────────────────────────────────────
# DualTrader 설치 스크립트 (macOS)
# ──────────────────────────────────────────────

set -e

echo "================================="
echo " DualTrader 설치 시작"
echo "================================="

# Python 버전 확인
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    echo "[오류] Python 3.11 이상이 필요합니다. 현재: $PYTHON_VERSION"
    echo "  brew install python@3.11"
    exit 1
fi
echo "[OK] Python $PYTHON_VERSION"

# 가상환경 생성
VENV_DIR="$(dirname "$0")/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[설치] 가상환경 생성 중..."
    python3 -m venv "$VENV_DIR"
fi
echo "[OK] 가상환경: $VENV_DIR"

# 가상환경 활성화
source "$VENV_DIR/bin/activate"

# 의존성 설치
echo "[설치] 패키지 설치 중..."
pip install --upgrade pip
pip install -r "$(dirname "$0")/requirements.txt"

# .env 파일 확인
ENV_FILE="$(dirname "$0")/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "[주의] .env 파일이 없습니다."
    echo "  cp .env.example .env"
    echo "  그 후 API 키를 입력하세요."
    cp "$(dirname "$0")/.env.example" "$ENV_FILE"
fi

# matplotlib 한글 폰트 설정 (macOS)
echo "[설정] matplotlib 한글 폰트 확인..."
python3 -c "
import matplotlib
import matplotlib.font_manager as fm
# macOS 기본 한글 폰트
fonts = [f.name for f in fm.fontManager.ttflist if 'Apple' in f.name or 'Gothic' in f.name or 'Nanum' in f.name]
if fonts:
    print(f'  한글 폰트 발견: {fonts[0]}')
else:
    print('  [주의] 한글 폰트가 없습니다. 나눔폰트를 설치하세요:')
    print('    brew install font-nanum-gothic')
" 2>/dev/null || true

echo ""
echo "================================="
echo " 설치 완료!"
echo "================================="
echo ""
echo "사용법:"
echo "  source venv/bin/activate"
echo "  python main.py --screen     # 종목 스크리닝 테스트"
echo "  python main.py --report     # 리포트 생성 테스트"
echo "  python main.py --paper      # 페이퍼 트레이딩 시작"
echo "  python main.py              # 자동매매 시작"
echo ""
