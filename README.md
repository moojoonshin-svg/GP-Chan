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

`run_pet.bat`은 생성된 에셋이 없을 때만 에셋을 빌드한 뒤 `pythonw`로 펫을 실행합니다.

## Controls

- 왼쪽 클릭: 짧은 랜덤 반응
- 왼쪽 드래그: 캐릭터 이동 및 `대롱대롱`
- 캐릭터 위 스크롤: `간지러워!`
- 오른쪽 클릭: 액션 선택, 크기 조절, 마우스 따라가기 설정, 종료

## Actions

| 액션 | 자막 |
|---|---|
| `idle` | 멍때리는 중 |
| `wave` | 하이 |
| `think` | 생각 중 |
| `typing` | 타닥타닥 |
| `cheer` | 힘내 지피짱 |
| `sit` | 쉬는 중 |
| `sleep` | 자는 중 |
| `pout` | 삐진 중 |
| `surprise` | 꺄악 |
| `sweep` | 청소 중 |
| `walk` | 산책 중 |
| `half_right` | 반만 맞습니다 |
| `welcome_agi` | AGI 즈라 |
| `agi_box` | 박스행 |
| `drag_dangle` | 대롱대롱 |
| `scroll_tickle` | 간지러워! |

## Project Structure

- `pet.py`: 데스크톱 펫 실행 코드
- `run_pet.bat`: Windows용 간단 실행 스크립트
- `requirements.txt`: Python 의존성
- `scripts/build_pet_assets.py`: 에셋 생성 스크립트
- `assets/source/`: 원본 스프라이트 시트
- `assets/generated/frames/<action>/`: 액션별 프레임 PNG
- `assets/generated/sprite_sheet.png`: 생성된 통합 스프라이트 시트
- `assets/generated/manifest.json`: 액션 및 프레임 정보

## Development

에셋을 다시 생성하려면 다음 명령을 실행합니다.

```bash
python scripts/build_pet_assets.py
```

문법 확인:

```bash
python -m py_compile pet.py scripts/build_pet_assets.py
```
