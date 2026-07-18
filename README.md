# production_AI

AI 숏드라마 영상 자동화 프로덕션 리포.

## Skill: `short-drama-production`

`.claude/skills/short-drama-production/` — 시나리오 → 에셋 → 샷리스트 → Higgsfield 생성까지의
표준 파이프라인 skill. 새 작품/에피소드에 그대로 재사용한다.

- `SKILL.md` — 파이프라인 전체 워크플로 (0~5단계)
- `assets/*.template.json` — 산출물 3종 스키마 템플릿 (asset manifest / scene / RUN_MANIFEST)
- `references/clip-prompt-template.md` — 클립 프롬프트 13섹션 템플릿 + 완성 예제
- `references/example-empress-ep01/` — 검증된 레퍼런스 구현 (EMPRESS SELECTION EP01)

사용법: 이 리포가 열린 세션에서 시나리오를 주고 "이 시나리오로 파일럿 프로덕션 만들어줘"라고
요청하면 skill이 트리거되어 `<project>_production/` 폴더에 표준 산출물을 생성한다.
