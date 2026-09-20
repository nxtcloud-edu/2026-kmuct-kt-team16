# Snaptok MVP 진행 상황 (PROGRESS)

이 파일은 세션 인수인계용이다. 새 세션(계정이 바뀌어도)은 `SNAPTOK_MVP_PROMPT.md`와 이 파일만 읽고 이어갈 수 있어야 한다.
작업 하나가 끝날 때마다: 테스트 실행 → 이 파일 갱신(완료 작업 / 테스트 결과 / 다음 작업 / 주의사항) → 5줄 이내 보고 → 멈춤.

---

## 현재 상태 (해커톤 시간제약 모드)

- **완료**: T1~T7 + T8(서버 수정/되돌리기/resolve API 구현·기존 43테스트 통과) + 웹 최소 연결 + 샘플 3장.
- **다음 작업(미완)**: 웹 데이터계층 완전 교체(T9), 위치시스템 전면 통합(T11), 앱내 시간알림(T12), 날짜상수 교체, 구글캘린더(T15), 카카오(T14), 평가스크립트(T16), 결산요약(T17), 브라우저 실측 스크린샷 검증.
- **서버 실행**: cwd=`server`, `.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000` → 웹 http://localhost:8000/app/ . 시드 초기화 `python seed.py --reset`.

### 웹 연결 요약(Snaptok/app.js, localStorage 유지)
- `analyzeOne(file)`: claude 제거 → `POST /api/analyze`(FormData image+request_id). 서버가 분석·저장하고 응답의 `results[].item`(geoType/lat/lng/radius/area/brand/branches/expiry/geo_enabled 포함)을 반환.
- `runAnalysis`: 분석 즉시 `applyServerResults`로 localStorage 저장(addEventAuto/addLibraryAuto), 결과 시트는 [확인] 버튼 하나(`showResult`). 서버 오류/review → pendingReview(확인 필요).
- `addLibraryAuto`: geoType/lat/lng/radius/area/brand/branches/expiry/used 를 record 에 저장 → 지오펜스 엔진이 새 항목 감시.
- `#push` 배너: "캘린더 N건 · 보관함 N건 · 확인 필요 N건" + 위치등록 시 "{이름} · 근처에 가면 알려드릴게요".
- "지금 이 주변" 카운트 = geoTargets(=library 중 geoType 보유) 기준. 시드 trigger(trig-seed-sbux) 제거.
- `fileToCompressed` 기본 800px/0.7. `checkAiCapability`는 /api/health 로 mock/live 표시.
- `node --check app.js` EXIT=0(문법 OK).

### 서버 검증(빈 상태 아님, 시드 위에서 3샘플 업로드 결과)
- yeonnam_pasta_food → memory, geoType=specific lat37.5663 geo_enabled=True → geoTargets 등장 ✓
- contest_ideathon → action, 일정 2건(접수마감+본선발표) ✓
- starbucks_coupon → action 일정1건 저장 + 보관함쿠폰은 **시드 seed-coupon-sbux 와 제목 중복**이라 "중복 건너뜀"(빈 DB에선 이중저장 정상, T6/T7 테스트 PASS). 시연 시 스벅 쿠폰 새로 생기게 하려면 시드 쿠폰 제거 또는 빈 DB.

### T8 서버 API(구현·기동 확인, 추가테스트는 시간상 생략)
- store.py: undo_recent(payload 연쇄삭제+이미지정리), delete_event/delete_library, update_library(title/category/note/geo_enabled/used), set_library_location(lat/lng 명시지정→geo_enabled), resolve_review(schedule|memory|delete, extracted 재사용 재-LLM없음).
- main.py: PATCH /api/library/{id}, POST /api/library/{id}/location, DELETE /api/library|events/{id}, POST /api/review/{id}/resolve, POST /api/recent/{id}/undo.
- **사용자 확인 대기(비차단)**: 실제 Anthropic 키로 live 분석 확인은 사용자가 `server/.env` 에 `LLM_API_KEY` 채운 뒤 진행(T5 mock 은 완료). 실제 모델명(`claude-sonnet-5`)이 유효하지 않으면 `.env` 의 `LLM_MODEL` 만 바꾸면 됨.

## 작업 목록 (P0 → P1 → P2)

### P0 (이것만으로 시연 가능)
- [x] **T1** 저장소 정리: `git init`, `.gitignore`, `docs/PROGRESS.md`
- [x] **T2** 웹 리팩터링: index.html → assets/styles.css/app.js 분리, `index.original.html` 보존 (동작 동일)
- [x] **T3** 서버 뼈대: FastAPI, SQLite(SQLAlchemy) 모델, 이미지 저장, `/app` 정적 제공, `.env.example`
- [x] **T4** `/api/state` + 시드 스크립트 (데모 시드 데이터를 서버로, `seed:true`)
- [x] **T5** LLM 추상화 계층 + 분석 프롬프트/JSON 파싱 (재시도, mock 모드)
- [x] **T6** `/api/analyze` 라우팅·저장 규칙 (근거검사, 지난날짜, 쿠폰 이중저장, 중복, 멱등) + 서버 테스트
- [x] **T7** 장소 좌표화 (시드 대체 경로 포함), geo_enabled 자동 설정 + 테스트
- [ ] **T8** 되돌리기/삭제 연쇄 + review resolve + 테스트
- [ ] **T9** 웹 데이터 계층 교체 (state 로드, API 연동, 실패 토스트/롤백, 이미지 URL)
- [ ] **T10** 웹 자동 저장 결과 시트 (배지·되돌리기·분류변경, [확인], 요약 배너)
- [ ] **T11** 웹 위치 시스템 통합 + 지오펜스 순수함수 node 테스트
- [ ] **T12** 웹 시간 알림 + 날짜 처리 (TODAY 제거, 시연날짜, 월 이동)
- [ ] **T13** 시연 샘플 이미지 + 기대 결과 JSON

### P1
- [ ] **T14** 카카오 장소 검색(서버 REST) + 웹 JS SDK 브랜드 매장 찾기
- [ ] **T15** 구글 캘린더 동기화
- [ ] **T16** HTTPS 실기기 테스트 문서 + 평가 스크립트

### P2
- [ ] **T17** 결산 AI 요약 `/api/wrapped-summary`, 검색 개선

---

## 결정된 설정 / 주의사항

- **LLM**: Anthropic Claude. `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-sonnet-5` (모델명은 환경변수로 교체 가능).
- **API 키**: 사용자가 `server/.env`에 직접 입력한다. **키를 채팅으로 요구하거나 코드·커밋에 넣지 않는다.** `server/.env`는 `.gitignore`에 포함됨.
- **mock 모드**: 키가 없어도 테스트가 돌도록 LLM 호출에 mock 모드를 둔다. 단위 테스트는 mock으로 실행. 실제 키 확인은 T5에서 사용자가 `.env`를 채운 뒤 진행.
- **환경**: Windows(PowerShell). Python 3.11.4 확인됨. git 2.55.0. 저장소 루트 `C:\Users\82108\snaptok_v2`.
- **범위 제한**: 저장소 루트 밖(특히 `C:\Users\82108\snaptok`, `Snaptok-v8`)은 읽거나 수정하지 않는다. `Snaptok/` 폴더 이름은 바꾸지 않는다.
- **진행 규칙**: 작업은 작게, 각 작업 후 테스트→PROGRESS 갱신→보고→멈춤. 자동으로 다음 작업으로 넘어가지 않는다. 승인 없이 파일 삭제 금지.
- **위치 프라이버시**: 사용자 위치는 Snaptok 서버로 보내거나 저장하지 않는다. 지오펜스 판단은 브라우저 안에서만.

## 테스트 결과 기록

- **T1**: (테스트 대상 코드 없음) `git init` 완료, `.gitignore`/`docs/PROGRESS.md` 생성 확인.
- **T2**: 동등성 검증 통과. 원본 `<style>` 본문 == `styles.css` (완전 동일), 원본 `<script>` 본문(자산 base64 2개를 경로로 치환한 것 제외) == `app.js` (완전 동일). JS 괄호/중괄호 균형 확인. 코드 로직은 한 글자도 변경 없음(순수 추출·치환).

## T2 결과 상세 (Snaptok/ 구조)

- `index.html`: 265KB → 6KB. `<head>`에 `<link rel="stylesheet" href="styles.css">`, `</body>` 앞에 `<script src="app.js"></script>`.
- `styles.css`: 원본 `<style>` 본문(16KB).
- `app.js`: 원본 `<script>` 본문(51KB 코드). `LOGO_DATA='assets/logo.png'`, 시드 해커톤 일정의 `image:'assets/hackathon.jpg'`로 참조 변경.
- `assets/logo.png`(48KB, 원래 LOGO_DATA base64 PNG), `assets/hackathon.jpg`(89KB, 시드 포스터 base64 JPEG).
- `index.original.html`: 원본 백업(수정 금지, 재실행 시 덮어쓰지 않음).
- 파일 인코딩은 UTF-8(BOM 없음). PowerShell 콘솔에서 한글이 깨져 보이면 코드페이지 문제이니 Python(`open(..., encoding='utf-8')`)으로 읽을 것.
- 자산은 상대경로라 `/app` 정적 제공(같은 폴더) 또는 같은 폴더 `file://`에서 정상 로드. T3에서 `/app`로 서빙 예정.

## T3 결과 상세 (server/ 구조)

- **스택**: Python 3.11 venv(`server/.venv`), FastAPI 0.115.6, SQLAlchemy 2.0.36, uvicorn, python-multipart, python-dotenv, httpx, pydantic, pytest. `server/requirements.txt` 참고.
- **의존성 설치**: `server/.venv` 에 설치 완료(EXITCODE=0). 파이썬 실행은 `server\.venv\Scripts\python.exe`.
- **파일**:
  - `server/app/config.py`: `.env`(server/.env) 로드, 명세 4절 전체 환경변수 → `settings` 객체. 경로 상수(WEB_DIR=Snaptok/, DATA_DIR, IMAGES_DIR, DB_PATH, PLACES_SEED_PATH). `settings.llm_enabled`(키 있으면 live, 없으면 mock), `settings.calendar_sync_enabled`.
  - `server/app/db.py`: SQLite 엔진(`server/data/snaptok.db`), `SessionLocal`, `init_db()`, `get_session()` 의존성. data/images 디렉터리 자동 생성.
  - `server/app/models.py`: 테이블 5개 — `events`, `library`(geo_type/lat/lng/radius/brand/expiry/geo_enabled/missed/used 포함), `review`(extracted=LLM원본JSON), `recent`(payload=연쇄삭제 대상 id들, undone), `processed_request`(request_id 멱등, result JSON). 지오펜스 실행상태·사용자좌표는 저장 안 함(주석 명시).
  - `server/app/images.py`: `save_image_bytes()`(uuid+확장자), `image_path()`(경로이탈 차단), `content_type_for()`.
  - `server/app/main.py`: lifespan에서 `init_db()`, `/api/health`, `/api/images/{id}`, `/`(안내), `/app` StaticFiles(html=True) 마운트(API 라우트 뒤).
  - `server/.env.example`: 명세 4절 환경변수 예시(키는 비움).
- **실행 방법**: `server\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000` (cwd=server). 웹은 http://localhost:8000/app/ , health는 /api/health.
- **스모크 테스트 결과**: 전부 PASS — health(mock 모드), 없는 이미지 404, 경로이탈(../) 차단, /app/·styles.css·app.js·logo.png 200, 5개 테이블 생성. (1회성 스크립트라 삭제함.)
- **주의**: starlette `TestClient(app)`는 `with` 블록(또는 `__enter__`) 안에서만 lifespan(init_db)이 실행됨. 후속 pytest에서 앱 테스트 시 `with TestClient(app) as c:` 사용하거나 픽스처에서 `init_db()` 직접 호출할 것. 실제 uvicorn 실행에서는 lifespan 정상 동작.

## T4 결과 상세 (/api/state + 시드)

- **모델 추가 필드**: Event/Library/Review 에 `display_image`(시드·데모 표시용 SVG data URI 또는 상대경로. 업로드분은 None 이고 image_id 사용), Library 에 `thumb`(이모지), `branches`(brand 매장 좌표 JSON). Recent 에 `detail`, `display_image`, `kind_ref`(데모 refId).
- **이미지 표시 규칙(serializers.py)**: image_id 있으면 `/api/images/{id}`, 없으면 display_image 를 그대로 `image` 로. 웹은 `item.image` 만 쓰면 됨(시드는 SVG, 업로드분은 URL).
- **seed_data.py**: app.js 시드와 동일. `poster_svg()` 는 app.js `posterSVG` 와 동일 SVG + `encodeURIComponent` 호환 인코딩(`quote(svg, safe="!~*'()")`). 시드 개수: events 9, library 13, recent 5.
- **seed.py**: `python seed.py` (기존 seed=true 만 삭제 후 재삽입, 멱등) / `python seed.py --reset` (drop_all 후 전체 재생성). 모든 시드 `seed=true`(recent 는 id `r-seed-*`). 실제 DB(server/data/snaptok.db)에 시드 채워둠.
- **/api/state** 응답: `{events[], library[], review[], recent[], geoTargets[], config{demo_today,default_timezone,calendar_sync}}`. events=날짜asc, library/review/recent=created_at desc(recent는 undone=false, 최대60). **geoTargets = geo_enabled 이고 used=false 이고 (brand 또는 lat/lng 있음)** 인 library. 시드 geoTargets 5개(sbux brand, 파스타 연남/성수/역삼, 성수 미디어아트전시).
- **웹 필드 매핑**: library 는 `place`(=place_name), `geoType`, `geo_enabled`, `branches`, `expiry`, `missed`, `used` 등. recent 는 `label`(=summary), `detail`, `refId`(=kind_ref), `ts`(created_at ms). 좌표 시드: 연남 37.5663/126.9254, 성수 37.5446/127.0559, 역삼 37.5015/127.0380, 스벅 매장 3곳.
- **테스트 결과**: 전부 PASS(시드 개수, 재시드 무중복, /api/state 구조/개수, geoTargets 5개, sbux branches 3·brand·expiry, 해커톤 이미지 경로, 파스타 SVG data URI·좌표, config). (1회성 스크립트 삭제함.)

## T5 결과 상세 (LLM 추상화 계층 server/app/llm/)

- **구조**: `llm/__init__.py`(get_provider: settings 기반, 키없음/미지 provider→mock), `base.py`(AnalysisProvider Protocol, AnalysisResult{data,raw,parsed,mode}), `prompt.py`(CATEGORIES 11개, OUTPUT_SCHEMA, build_system_prompt/build_user_prompt), `schema.py`(파싱·정규화·UNCERTAIN 폴백), `anthropic_provider.py`(live), `mock_provider.py`(오프라인/테스트).
- **analyze 시그니처**: `analyze(image_bytes, content_type, captured_at, today, timezone, hint=None) -> AnalysisResult`. hint=파일명 등(선택). live 는 무시, mock 은 오프라인 분류에 사용(특정 이미지 하드코딩 아님, 일반 키워드 규칙).
- **schema.normalize/parse_response**: 코드펜스 제거 후 첫 {..} JSON 로드. type 검증(ACTION/MEMORY/UNCERTAIN, 아니면 UNCERTAIN), confidence 0~1 클램프, category 11개 아니면 '기타', item.date 가 YYYY-MM-DD 아니면 그 item 제거(없는 날짜 방지), time/end_time HH:MM 검증. `parse_response(text)->(dict, ok)`, 파싱실패면 (UNCERTAIN, False).
- **anthropic_provider**: POST https://api.anthropic.com/v1/messages, 헤더 x-api-key+anthropic-version 2023-06-01, content=[image(base64), text]. 파싱 실패 시 1회 재시도(JSON강조), 그래도 실패면 UNCERTAIN. 네트워크/HTTP 오류는 예외 전파(T6 라우트에서 "분석 실패"로 처리 예정). 키는 settings 에서만.
- **mock_provider**: 힌트 키워드로 분류 — 쿠폰/기프티콘/스타벅스→ACTION 쿠폰(use,expiry=today+5,brand), 맛집/파스타(+연남/성수/역삼)→MEMORY 맛집, 공모전/아이디어톤→ACTION 2건(deadline today+7 + event today+9), 해커톤→ACTION 1건(event, 마감없음), 전시/팝업→MEMORY 전시회, 여행→MEMORY 여행지, 패션→MEMORY 패션, 세미나/애매→UNCERTAIN, 밈/기타→MEMORY 기타, 힌트없음/미매칭→UNCERTAIN(없는 날짜 생성 안 함). 날짜는 today 기준 상대라 결정적.
- **테스트**: `server/tests/test_llm.py` 15개 전부 PASS(pytest). `server/pytest.ini`(testpaths=tests). 실행: cwd=server, `.venv\Scripts\python.exe -m pytest tests/test_llm.py`.
- **live 확인 방법(사용자)**: server/.env 에 LLM_API_KEY 입력 후 `.venv\Scripts\python.exe -m uvicorn app.main:app` 실행 → /api/health 의 llm_mode 가 live 인지 확인. 모델명 유효하지 않으면 LLM_MODEL 만 교체.

## T6 결과 상세 (/api/analyze + 라우팅)

- **dedup.py**: 바이그램 Dice 유사도(app.js 동일). `norm_title`(소문자+공백/특수문자 제거), `bigrams`, `similarity`, `is_duplicate`(THRESHOLD=0.55).
- **routing.py (순수 함수, DB 없음)**:
  - `evidence_supported(item, visible_text)`: date 의 월·일 숫자가 visible_text 에 있어야 하고(최소 '일'), evidence 가 있으면 evidence 에도 '일' 숫자 있어야 함 → 지어낸 날짜 거부.
  - `is_past(item, now)`: expiry=만료일23:59, event=end_time(없으면 time, 없으면 23:59), deadline=time(없으면 23:59) 기준으로 now 와 비교.
  - `title_with_action(title, action_type)`: "{title} · {행동}" (apply=신청/submit=제출/use=사용/book=예약/attend=참석/pay=결제).
  - `plan_routing(data, now, CA, CM) -> RoutingPlan(decision, events[], library[], review, valid_items)`: ACTION&conf>=CA&유효항목있음→일정(지난건 보관함 missed, use면 일정+보관함쿠폰[category쿠폰,brand면 geo_type=brand,expiry]), MEMORY&conf>=CM→보관함, 그외→review(사유: 확신도낮음/근거있는날짜없음/날짜역할불분명).
- **store.py (DB 반영)**: `apply_plan(db, plan, image_id, display_image, extracted, source_label)`. 일정 중복=같은 date+유사도0.55, 보관함 중복=같은 category+유사도0.55 → 중복이면 status=dup(badge "중복 건너뜀"). 저장 성공 배지: 캘린더 저장됨/보관함 저장됨/보관함 쿠폰/지난 마감/확인 필요. RecentActivity(kind=analyze, payload=created{events,library,review} JSON) 로 되돌리기 연쇄 대상 기록. review 는 extracted(정규화 JSON) 보관 → T8 resolve 시 재-LLM 불필요. `store._attach_location(item)` 은 geocode 모듈 있으면 호출(T7 에서 구현).
- **/api/analyze** (multipart: image, captured_at?, request_id?): 멱등(ProcessedRequest 에 결과 JSON 저장·재사용), 이미지 파일 저장(image_id), `_resolve_today_now()`(DEMO_TODAY 있으면 그 날짜+현재시분을 now 로), provider.analyze(hint=filename), 예외 시 "분석 실패"→review. 응답: {request_id, decision, results[], summary, recent_id, image, llm_mode}.
- **_resolve_today_now**: DEMO_TODAY=2026-09-20 이면 today="2026-09-20", now=그 날짜+현재 시분. 없으면 실제 오늘.
- **테스트**: test_routing.py(12) + test_analyze.py(8) + test_llm.py(15) = **전체 35개 PASS**. 실행: cwd=server, `.venv\Scripts\python.exe -m pytest`. conftest 는 각 테스트마다 drop_all+init_db(빈 DB). **주의: 테스트가 DB 를 비우므로 테스트 후 `python seed.py --reset` 로 재시드해야 데모 데이터 복구됨**(T6 후 재시드 완료).

## T7 결과 상세 (장소 좌표화 geocode.py)

- **data/places_seed.json**: 시연용 근사 좌표. `places`(keywords/name/area/lat/lng/kind: specific|area) + `brand_stores`(스타벅스 3매장). 연남/성수/역삼 파스타(specific), 연남동/성수/역삼 중심(area).
- **geocode.py**:
  - `resolve_coordinates(geo_type, place_name, area, brand, category) -> {geo_type, lat, lng, radius, branches, geo_enabled}` (순수 함수).
  - brand → geo_type=brand, branches=시드 매장, geo_enabled=True(쿠폰 brand 기본 on), 좌표는 None(매장은 웹이 현재위치로 찾음).
  - 해외(교토/도쿄/파리 등 _OVERSEAS_HINTS) → 좌표 없이 geo_enabled=False.
  - specific(place_name 있음) → kakao_search(미구현시 None)→ 시드 lookup, radius=150, geo_enabled=category∈{맛집,여행지,전시회,패션,콘서트,쿠폰}.
  - area(동네만) → 시드 area 중심, radius=700, 같은 카테고리 규칙.
  - 못 찾음 → 좌표 없이 geo_enabled=False.
  - `attach_location(item)`: LibraryItem 의 geo_type/lat/lng/radius/branches(JSON)/geo_enabled 를 in-place 로 채움. store.apply_plan 의 _attach_location 훅이 저장 직전 호출.
  - `kakao_search(query)`: T14(P1) 에서 실제 카카오 REST 구현. 지금은 키 없으면/미구현 None → 시드 대체.
- **GEO_CATEGORIES** = {맛집, 여행지, 전시회, 패션, 콘서트, 쿠폰}. 공부 등은 좌표 붙어도 geo_enabled=False.
- **테스트**: test_geocode.py(6) + 통합 2건(analyze 후 맛집 좌표/geoTargets, 쿠폰 brand/branches/geoTargets) = **전체 43개 PASS**. 테스트 후 재시드 완료(events 9/library 13 확인).
