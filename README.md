# GPZZ Desktop Pet

작업 폴더 안의 기준 시트를 바탕으로 `80x80` 프레임 자산을 만들고, 그 프레임을 재생하는 파이썬 데스크톱 펫입니다.

## 실행

```bash
python scripts/build_pet_assets.py
python pet.py
```

## 구성

- `assets/source/gpzz_sheet_green.png`: 생성된 기준 포즈 시트 원본
- `assets/generated/frames/<action>`: 액션별 8프레임 PNG
- `assets/generated/sprite_sheet.png`: 10개 액션을 합친 최종 시트
- `assets/generated/manifest.json`: 앱이 읽는 프레임 정보
- `pet.py`: 항상 위에 떠 있는 드래그 가능한 데스크톱 펫

## 조작

- 왼쪽 클릭: 짧은 리액션 액션 실행
- 드래그: 위치 이동
- 오른쪽 클릭: 액션 직접 선택 또는 종료
