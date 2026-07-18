# 클립 프롬프트 13섹션 템플릿 (Seedance 계열 영상 모델용)

클립당 1개 `.txt` 파일. 섹션 헤더는 영어 대문자 그대로, 본문도 영어로 쓴다.
섹션 순서를 바꾸지 말 것 — 모델이 앞쪽 섹션(컨텍스트→레퍼런스→공간)을 기반으로
뒤쪽 섹션(카메라→연기→조명)을 해석한다.

`duration`과 `aspect_ratio`는 프롬프트에 쓰지 않는다 — Higgsfield `generate_video`의
생성 파라미터로만 전달한다.

## 섹션별 작성 요령

| 섹션 | 내용 | 요령 |
|------|------|------|
| SCENE CONTEXT | 이 컷이 이야기의 어떤 순간인지 2~3문장 | 인물 관계·상황을 모델에게 납득시키는 부분. 연출 지시는 쓰지 않음 |
| ACTIVE REFERENCES | 컷에 등장하는 @핸들별 1줄 외형 요약 | 각 줄 끝에 "100% matches the reference." 고정 문구. 인물 3개 이하 |
| LOCATION MAP | Foreground / Midground / Background + 카메라 위치 + 광원 방향 | 공간을 레이어로 서술하면 배치 오류가 급감 |
| FIRST FRAME / BLOCKING | 첫 프레임에 정확히 뭐가 보이는지 | 세로 구도 명시. 첫 프레임이 어긋나면 컷 전체가 어긋남 |
| FORMAT MODE | "One continuous shot, the camera does not cut on its own." | 모델의 임의 컷 편집 방지. 원샷 기본 |
| OPTICS | 화각(압축)·심도·보케 | 예: "29° portrait compression, shallow depth of field" |
| CAMERA | 카메라 이동을 시간 순으로 | 시작 위치·이동 경로·종료 프레이밍·속도. 샷리스트 `cam` 필드를 풀어쓴 것 |
| ACTION | 인물의 물리적 동작을 시간 순으로 | 미세하게, 정량적으로 ("chin lifts two centimeters") |
| PERFORMANCE | 표정·감정·시선 | "no drift in facial identity" 류의 아이덴티티 고정 문구 포함 |
| LIGHTING | 키/림 광원·색온도 | 룩바이블(scene.json `look.wb`)과 반드시 일치 |
| AUDIO | VO/대사(영어 1문장) + 앰비언스 | 샷리스트 `audio` 필드와 동일 문장 |
| STYLE | 장르 룩 1줄 | 전 클립 동일 문구 유지 (룩 통일) |
| POSITIVE LOCKS | 깨지면 안 되는 것들을 긍정문으로 | 아래 참조 |

## POSITIVE LOCKS 작성 규칙

부정문("no text", "don't change her face")이 아니라 **유지되는 상태를 긍정문으로** 쓴다:

- `Her appearance matches @Lionella exactly in every frame.`
- `The screen stays free of any text or captions.`
- `The hall stays empty of other people.`
- 스크린 방향 락이 걸린 컷이면: `She stays on the right side of frame, looking left.`

생성 실패·붕괴 시 재시도할 때는 이 섹션에 락을 추가·보강하는 방식으로 대응한다 (1회 재시도 원칙).

## 완성 예제 (EMPRESS EP01 · C01 콜드 오픈, 10s)

```
SCENE CONTEXT
An imperial coronation-selection ceremony begins. A young royal woman stands alone just inside the massive bronze doors of a vast marble cathedral, facing down the crimson carpet toward a distant throne.

ACTIVE REFERENCES
@Lionella: mid-20s royal woman, platinum ash-blonde ceremonial updo, white silk gown with silver embroidery, diamond tiara with a teardrop stone. 100% matches the reference.
@GrandCathedral: marble cathedral throne hall, crimson carpet, stained-glass light shafts, standing candelabra. 100% matches the reference.

LOCATION MAP
Foreground: polished marble floor and the hem of her white gown. Midground: @Lionella standing centered on the crimson carpet. Background: columns receding toward the gilded throne, sapphire and ruby light shafts through incense haze at 20% density. Camera near the floor in front of her. Light from candelabra both sides and colored windows high left.

FIRST FRAME / BLOCKING
Frame opens on her white slippers and gown hem on crimson carpet, centered, vertical composition.

FORMAT MODE
One continuous shot, the camera does not cut on its own.

OPTICS
29° portrait compression throughout, no drift mid-shot. Shallow depth of field, background candles dissolve into round bokeh.

CAMERA
Starts at ankle height 1.5 meters from her, tilts up smoothly along the gown, the bodice, the diamond tiara, ending framed on her face in the upper third. Tilt speed steady and ceremonial, completing in the final second.

ACTION
She stands perfectly still through the tilt. As the frame reaches her face, her chin lifts two centimeters and her eyes open from a slow blink, gaze fixed far ahead toward the throne.

PERFORMANCE
Neutral regal mask with a faint cold edge at the mouth corner. Catch-lights from candle flames in both eyes. Visible fine skin texture, no drift in facial identity.

LIGHTING
Warm candle key at 3200K from both sides, cool sapphire window spill as rim on her hair and tiara. Haze holds the light shafts visible.

AUDIO
Female voice-over, low and calm: "Five years ago today, I became Empress here." Distant cathedral ambience, a single deep bell.

STYLE
Photoreal, high-end romantic fantasy, fine film grain, jewel-tone palette.

POSITIVE LOCKS
Her appearance matches @Lionella exactly in every frame. The tiara stays centered on her forehead. The hall stays empty of other people. The screen stays free of any text or captions.
```
