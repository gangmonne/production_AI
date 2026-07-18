---
name: short-drama-production
description: >
  AI 숏드라마(세로 숏폼 드라마) 영상 자동화 프로덕션 파이프라인. 시나리오(대본/작품 카드)를 입력받아
  ①분석·파일럿 선정 → ②에셋 매니페스트 → ③씬/샷리스트 JSON → ④클립 프롬프트 → ⑤Higgsfield MCP로
  이미지(캐릭터·배경 레퍼런스)와 영상 클립을 생성하는 전 과정을 표준 산출물로 만들어낸다.
  사용자가 새 시나리오/작품/에피소드로 "파일럿 만들어줘", "영상 제작 준비해줘", "프로덕션 돌려줘",
  "에셋 뽑아줘", "샷리스트 만들어줘", "숏드라마 파이프라인 적용해줘"라고 하거나, ReelShort/DramaBox류
  숏드라마 콘텐츠 제작·Seedance/nano_banana 영상 생성·기존 RUN_production 스타일 산출물 갱신을
  요청하면 반드시 이 skill을 사용할 것. 시나리오 문서(docx 등)만 던져주며 영상화를 언급해도 트리거.
---

# AI 숏드라마 프로덕션 파이프라인

시나리오 텍스트를 받아 Higgsfield MCP 생성까지 이어지는 **재사용 가능한 표준 프로세스**다.
어떤 작품이든 산출물 스키마는 동일하게 유지하고, 내용(asset_map·프롬프트·샷리스트)만 교체한다.
검증된 레퍼런스 구현이 `references/example-empress-ep01/`에 있다 — 각 단계에서 형식이 헷갈리면
해당 예제 파일을 먼저 읽고 그대로 따라갈 것.

## 산출물 구조 (프로젝트당 1폴더)

```
<project>_production/
├── 00_analysis.md            # 시나리오 분석 + 파일럿 선정 + 포맷 결정 + 룩바이블
├── 01_asset_manifest.json    # @핸들 에셋(캐릭터/장소) + 이미지 생성 프롬프트
├── 02_<ep>.scene.json        # 씬 메타 + 룩 + 방향 락 + 샷리스트
├── 03_prompts/clipNN_*.txt   # 클립당 1파일, 13섹션 영상 프롬프트
├── RUN_MANIFEST.json         # Phase A/B/C 실행 계획 (기계가 읽는 발주서)
└── <ep>_pipeline_board.html  # 사람이 검토하는 파이프라인 보드
```

번호가 곧 실행 순서다. 앞 단계 산출물이 뒷 단계의 입력이므로 **순서를 건너뛰지 말 것** —
예: 에셋 핸들이 확정되기 전에 샷리스트를 쓰면 refs가 어긋난다.

## 0단계 — 시나리오 분석 (`00_analysis.md`)

입력: 시나리오 문서(docx/md/txt). 여러 작품이 묶여 있으면 표로 정리(작품·배경·핵심 트리거)한 뒤
**파일럿 1편을 선정**하고 근거를 명시한다. 선정 기준은 자동화 검증 효율:

- 등장 **공간 수가 적을 것** (에셋 최소 → 루프 검증 최적)
- 컷당 인물 태그 한도(기본 3인/컷) 안에서 설계 가능한 캐릭터 수
- AI 생성 강점 장르(의상·건축 비주얼이 힘을 쓰는 로판/판타지 등)와의 부합

분석 문서에 반드시 포함할 섹션:

1. **에피소드 비트 구조** — 러닝타임 목표(기본 120초 + 예고 5초)를 5비트로 분해:
   콜드 오픈 → 배경 압축 → 각성/전환 → 첫 반격(메인 시퀀스) → 클리프행어. 비트별 타임코드·내용·감정.
2. **포맷 결정 (자동화 스펙)** — 아래 기본값에서 시작하고, 바꿀 땐 이유를 기록:
   - 화면비 **9:16 세로** (ReelShort·DramaBox·FlexTV 표준)
   - 클립 단위: 영상 모델의 클립당 최대 길이(Seedance 2.0 = 15초)로 에피소드를 나눔 → 클립 수 산출
   - 대사: **영어 1문장/클립** (립싱크 안정성·글로벌 우선), 현지화판은 포스트 더빙
   - **화면 내 자막·텍스트 생성 금지** — 자막은 포스트에서 삽입 (생성 텍스트는 반드시 깨진다)
3. **스크린 방향 락** — 주인공과 상대 진영의 프레임 좌/우 위치·시선 방향을 에피소드 전체에서
   고정하고 명문화한다. 클립을 독립 생성하기 때문에 이 락이 없으면 편집 시 시선 축이 붕괴한다.
4. **룩바이블** — 장르 룩·팔레트, 공간별 조명 색온도, 카메라 문법(심도·앵글·프레임 내 얼굴 위치),
   장르 고유 문법(예: 응징물 = 주인공 로우앵글/가해자 하이앵글).
5. **확장 로드맵** — Phase 1(본 파일럿) / Phase 2(후속 에피소드+추가 에셋) / Phase 3(자매 작품 —
   동일 스키마에 asset_map만 교체).

## 1단계 — 에셋 매니페스트 (`01_asset_manifest.json`)

스키마: `assets/01_asset_manifest.template.json`. 핵심 규칙:

- 에셋마다 `@PascalCase` 핸들 부여 — 이후 모든 단계가 이 핸들로만 에셋을 지칭한다.
- `type`: `character` | `location` | `prop`(동물 등). 파일럿에 안 쓰는 에셋은
  `phase2_assets_deferred`로 미뤄 생성 비용을 아낀다.
- **캐릭터 프롬프트**: full-body reference, 정면 직립, 무표정에 가까운 중립 표정,
  plain seamless light-grey studio background, even soft lighting, photorealistic 8K.
  의상·머리·눈동자 색을 구체적으로 — 이 이미지가 전 클립의 아이덴티티 앵커가 된다.
- **장소 프롬프트**: vertical architectural plate, **empty of people**, 색온도 명시(룩바이블과 일치),
  9:16 구도 지시(예: 핵심 오브젝트를 상단 1/3에).
- 스튜디오 배경/중립 조명을 쓰는 이유: 장면 조명이 박힌 레퍼런스는 다른 조명의 컷에 넣었을 때
  영상 모델이 조명을 못 벗겨낸다.

## 2단계 — 씬/샷리스트 (`02_<ep>.scene.json`)

스키마: `assets/02_scene.template.json`. `meta`(러닝타임·화면비·영상 모델), `look`(룩바이블 요약),
`screen_direction_lock`, `asset_map`(핸들→한글 설명), `shotlist`로 구성.

샷리스트 작성 규칙:

- 컷 ID는 `C01`부터 순번. 비트당 1~3컷, 컷 길이는 모델 최대치(15초) 이하.
- `refs`에는 그 컷에 실제 등장하는 핸들만 — **인물 핸들은 컷당 3개 이하** (레퍼런스 태그 한도).
- `size`/`cam`은 촬영 용어로 짧게 (WS→CU tilt-up, OTS pair, lateral track 등).
- `dir`에 방향 락 준수 여부를 컷마다 기록.
- `audio`는 클립당 영어 1문장 (VO 또는 대사).
- `duration`·`aspect_ratio`는 **프롬프트 본문이 아니라 생성 파라미터**로 — 프롬프트에 넣으면 무시되거나 화면에 새겨진다.

## 3단계 — 클립 프롬프트 (`03_prompts/`)

컷마다 `clipNN_<slug>.txt` 1파일. 13섹션 고정 템플릿을 사용한다 —
**`references/clip-prompt-template.md`를 읽고** 섹션 순서·작성 요령·완성 예제를 따를 것.
섹션: SCENE CONTEXT / ACTIVE REFERENCES / LOCATION MAP / FIRST FRAME·BLOCKING / FORMAT MODE /
OPTICS / CAMERA / ACTION / PERFORMANCE / LIGHTING / AUDIO / STYLE / POSITIVE LOCKS.

## 4단계 — 실행 계획 (`RUN_MANIFEST.json`) 및 발주

스키마: `assets/RUN_MANIFEST.template.json`. 실행은 3-Phase:

**Phase A — 에셋 이미지** (`generate_image`, 기본 모델 `nano_banana_2`)
- 핸들당 `count: 2`로 발주 (검증된 효율 패턴 — 1장은 실패 리스크, 3장+는 낭비).
- **게이트**: 핸들당 1장을 사용자가 픽 → 픽된 이미지 UUID를 Phase B 레퍼런스로 바인딩.
  이 게이트를 건너뛰고 영상까지 자동 진행하지 말 것 — 에셋이 틀리면 전 클립을 다시 뽑는다.

**Phase B — 영상 클립** (`generate_video`, 기본 모델 `seedance_2_0`, `aspect_ratio: 9:16` 파라미터)
- **순차 발주**: C01 완료 확인 → C02 → … (병렬 발주는 실패 시 원인 격리가 안 된다).
- 실패 시: 해당 클립의 POSITIVE LOCKS를 보강해 **1회만 재시도**, 그래도 실패하면 사용자에게 보고.

**Phase C — 포스트** (수동 체크리스트로 기록)
- 클립 컨펌 편집(타깃 러닝타임), 자막 포스트 삽입, 현지화판 더빙 교체.

알려진 도구 제약 (RUN_MANIFEST의 `known_tool_constraints`에 항상 기록):
- 잡 참조는 **full UUID** 사용 (축약 ID는 실패)
- 샌드박스에서 `media_upload` 실패 가능 — 생성물은 MCP 내부 에셋 ID 체인으로만 연결
- Higgsfield MCP 커넥터가 대화에서 활성화되어 있어야 함 — 발주 전 확인, 비활성이면 사용자에게 요청

## 5단계 — 파이프라인 보드 (`<ep>_pipeline_board.html`)

사람 검토용 단일 HTML: 헤더(작품·포맷·방향 락·실행 전제) + 에셋 카드 그리드(핸들·역할·
`<details>`로 접은 프롬프트) + 컷리스트 테이블(컷·비트·길이·카메라·refs·오디오, 행마다
`<details>`로 접은 클립 프롬프트 전문). 다크 테마. 마크업 구조는
`references/example-empress-ep01/ep01_pipeline_board.html` 참조.

## 새 작품에 적용하는 법 (Phase 3 패턴)

스키마는 그대로 두고 내용만 교체한다: 새 `<project>_production/` 폴더를 만들고
0단계부터 다시 — 단, `screen_direction_lock`·포맷 결정·13섹션 템플릿·3-Phase 실행 구조는
작품이 바뀌어도 유지되는 파이프라인 불변량이다. 룩바이블과 asset_map만 작품 고유로 새로 쓴다.
