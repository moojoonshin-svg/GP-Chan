# GPZZ Desktop Pet

<p align="center">
  <img src="assets/generated/frames/idle/00.png" alt="GPZZ Desktop Pet" width="220">
</p>

지피짱이 데스크톱 위에서 움직이고 반응하는 Python/Tkinter 기반 데스크톱 펫입니다.
마우스, 키보드 입력, PC 상태에 맞춰 작은 리액션을 보여주고 CPU/RAM 사용량도 함께 표시합니다.

## Features

- 마우스 hover, 클릭, 드래그, 스크롤 반응
- 마우스 따라가기와 짧은 산책 액션
- 키보드 열타이핑 감지 후 `타닥타닥` 액션
- CPU/RAM 사용량 게이지 표시
- 상태 기반 자동 액션
- 듀얼 모니터 가상 화면 좌표 대응
- 우클릭 메뉴로 액션 선택, 배율 조절, 마우스 따라가기 설정
- green screen 제거, despill, 보수적 remaster 기반의 투명 PNG 에셋 파이프라인
- 확대 표시 시 `BILINEAR` 리샘플링으로 성능과 부드러움 균형 조정

## Requirements

- Windows
- Python 3.11 이상 권장
- Pillow

```bash
pip install -r requirements.txt
```

## Run

간단 실행:

```bash
run_pet.bat
```

직접 실행:

```bash
python scripts/build_pet_assets.py
python pet.py
```

`run_pet.bat`은 빌드용 `assets/source_mastered/`를 기준으로 실행하고, 생성된 에셋이 없을 때만 빌드한 뒤 `pythonw`로 펫을 실행합니다.

## Controls

- 왼쪽 클릭: 짧은 랜덤 반응
- 왼쪽 더블클릭: `딱밤` 피격 반응과 클릭 지점 타격 이펙트
- 왼쪽 드래그: 캐릭터 이동 및 `대롱대롱`
- 캐릭터 위 스크롤: `간지러워!`
- 오른쪽 클릭: 액션 선택, 크기 조절, 마우스 따라가기 설정, 종료

## Actions

| Preview | Action | Caption |
|---|---|---|
| <img src="assets/generated/frames/idle/00.png" alt="idle" width="80"> | `idle` | 멍... |
| <img src="assets/generated/frames/wave/00.png" alt="wave" width="80"> | `wave` | ㅎㅇ |
| <img src="assets/generated/frames/think/00.png" alt="think" width="80"> | `think` | 흠... |
| <img src="assets/generated/frames/typing/00.png" alt="typing" width="80"> | `typing` | 토큰입력중 / 타닥타닥 / 작성중 |
| <img src="assets/generated/frames/cheer/00.png" alt="cheer" width="80"> | `cheer` | 힘내 휴먼 / 할수있다 / 가보자 |
| <img src="assets/generated/frames/sit/00.png" alt="sit" width="80"> | `sit` | 절전중 / 쉬는중 / 잠깐휴식 |
| <img src="assets/generated/frames/sleep/00.png" alt="sleep" width="80"> | `sleep` | Zzz.. / 수면중 / 충전중 |
| <img src="assets/generated/frames/pout/00.png" alt="pout" width="80"> | `pout` | 억까임 |
| <img src="assets/generated/frames/surprise/00.png" alt="surprise" width="80"> | `surprise` | 어라? |
| <img src="assets/generated/frames/sweep/00.png" alt="sweep" width="80"> | `sweep` | 청소각 |
| <img src="assets/generated/frames/walk/00.png" alt="walk" width="80"> | `walk` | 순찰중 |
| <img src="assets/generated/frames/half_right/00.png" alt="half_right" width="80"> | `half_right` | 반만 맞습니다 |
| <img src="assets/generated/frames/welcome_agi/00.png" alt="welcome_agi" width="80"> | `welcome_agi` | AGI 가즈아 / AGI 즈라 / 특이점각 |
| <img src="assets/generated/frames/agi_box/00.png" alt="agi_box" width="80"> | `agi_box` | 박스행 |
| <img src="assets/generated/frames/drag_dangle/00.png" alt="drag_dangle" width="80"> | `drag_dangle` | 살려줘 |
| <img src="assets/generated/frames/scroll_tickle/00.png" alt="scroll_tickle" width="80"> | `scroll_tickle` | 아ㅋㅋ |
| <img src="assets/generated/frames/bonk/00.png" alt="bonk" width="80"> | `bonk` | 아야 / 딱콩! / 너무해 |

## Runtime Captions

| Situation | Caption |
|---|---|
| 시작 | 부팅완 |
| 따라가기 켜짐 | 추적 on |
| 따라가기 꺼짐 | 추적 off |
| 마우스 추적 중 | 추적중 |
| 마우스를 놓침 | 놓침ㅋ |
| 마우스가 가까움 | 왔냐 |
| 산책 중 | 순찰중 |
| 산책 종료 | 복귀완 |
| 타이핑 후 대기 | 한가함 |
| 드래그 후 놓음 | 살았다 |
| hover 진입 | ㅎㅇㅎㅇ |
| 활동 감지 | 일하는척 |
| 충전 중 | 충전 n% |
| 새벽 시간대 | 야간모드 |

## Project Structure

- `pet.py`: 데스크톱 펫 실행 코드
- `run_pet.bat`: Windows용 간단 실행 스크립트
- `requirements.txt`: Python 의존성
- `scripts/remove_green_and_despill.py`: 초록 배경 제거 및 green spill 정리 스크립트
- `scripts/remaster_assets.py`: 캔버스/구도/포즈를 유지하는 보수적 리마스터 스크립트
- `scripts/clean_green_spill.py`: 이전 실행명을 위한 호환 래퍼
- `scripts/build_pet_assets.py`: 에셋 생성 스크립트
- `assets/source_mastered/`: 리마스터된 빌드용 transparent PNG 스프라이트 시트
- `assets/generated/frames/<action>/`: 액션별 프레임 PNG
- `assets/generated/sprite_sheet.png`: 생성된 통합 스프라이트 시트
- `assets/generated/manifest.json`: 액션 및 프레임 정보

## Development

초록 배경 원본과 중간 정리본은 repo에서 제거했습니다. 실제 빌드는 `assets/source_mastered/`만 기준으로 합니다.

초록 배경 원본에서 다시 despill/remaster를 수행해야 하는 경우에만, 같은 경로 구조로 `assets/source_raw_green/`을 직접 준비한 뒤 1-2개 샘플 처리해 캔버스 크기와 프레이밍이 유지되는지 확인합니다.

```bash
python scripts/remove_green_and_despill.py --sample 2
python scripts/remaster_assets.py --sample 2
```

문제가 없으면 전체 에셋을 다시 생성합니다.

```bash
python scripts/remove_green_and_despill.py
python scripts/remaster_assets.py
python scripts/build_pet_assets.py
```

문법 확인:

```bash
python -m py_compile pet.py scripts/remove_green_and_despill.py scripts/remaster_assets.py scripts/clean_green_spill.py scripts/build_pet_assets.py
```

## Fork Additions

이 아래 항목들은 원본 저장소 설명에 섞지 않고, 이 포크에서 추가한 내용만 따로 정리한 섹션입니다.

### Codex Integration

- 실행 중인 사용자 프로필의 `.codex/state_*.sqlite`와 현재 프로젝트의 Codex 세션 JSONL을 읽기 전용으로 확인합니다.
- 현재 프로젝트와 연결된 Codex 스레드가 있으면 CPU/RAM 패널 위에 `CODEX` 박스가 추가됩니다.
- 패널에는 현재 세션 기준 `5시간 남은량`, `1주일 남은량`이 표시됩니다.
- Codex가 응답 중이거나 답변 본문을 남기면 펫 말풍선에 짧게 표시합니다.
- Codex가 설치되어 있지 않거나 현재 프로젝트와 연결된 스레드가 없으면 기존 CPU/RAM 패널만 표시됩니다.

### 추가 메뉴 옵션

- 오른쪽 클릭 > `Codex 표시`: 켜기 / 끄기 / 새로고침
- 오른쪽 클릭 > `윈도우 시작시 실행`: 현재 사용자 기준 Windows 시작 프로그램에 등록/해제합니다.

### EXE Build

포크 버전은 단일 실행 파일로도 빌드할 수 있습니다.

```bash
python -m PyInstaller --noconfirm --clean --windowed --onefile --name GP-Chan --add-data "assets/generated;assets/generated" pet.py
```

빌드 결과물:

- `dist/GP-Chan.exe`
