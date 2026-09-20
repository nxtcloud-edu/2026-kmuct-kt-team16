(() => {
const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const TODAY='2026-09-20';
const WD=['일','월','화','수','목','금','토'];
const CATEGORIES=['맛집','여행지','패션','쿠폰','전시회','공모전','생일','영화','콘서트','공부','기타'];
const CAT_EMOJI={'맛집':'🍽️','여행지':'✈️','패션':'👕','쿠폰':'🎟️','전시회':'🖼️','공모전':'🏆','생일':'🎂','영화':'🎬','콘서트':'🎤','공부':'📚','기타':'📁'};
const CAT_TINT={'맛집':'#FFE3D6','여행지':'#DCEFFB','패션':'#EDE6FB','쿠폰':'#FFEBD0','전시회':'#F6E4F4','공모전':'#E3ECFF','생일':'#FFE1EC','영화':'#E3E0FA','콘서트':'#FFE0E0','공부':'#E1F3E6','기타':'#EFEAE0'};

// ---------- mascot logo ----------
const LOGO_DATA='assets/logo.png';
$('#brandLogo').innerHTML = `<img src="${LOGO_DATA}" style="width:34px;height:34px;border-radius:9px"> <span>Snaptok</span>`;
$('#wrappedLogoImg').src = LOGO_DATA;
$('#profileBtn').onclick=()=>toast('프로필','설정 화면은 다음 버전에서 지원해요.');

// ---------- storage ----------
const KEYS={events:'snaptok_events_v15',library:'snaptok_library_v15',triggers:'snaptok_triggers_v15',recent:'snaptok_recent_v15',review:'snaptok_review_v15'};
function load(key,fallback){try{const v=JSON.parse(localStorage.getItem(key));return Array.isArray(v)?v:fallback}catch{return fallback}}
function saveAll(){
  try{localStorage.setItem(KEYS.events,JSON.stringify(events));
  localStorage.setItem(KEYS.library,JSON.stringify(library));
  localStorage.setItem(KEYS.triggers,JSON.stringify(triggers));
  localStorage.setItem(KEYS.recent,JSON.stringify(recent));
  localStorage.setItem(KEYS.review,JSON.stringify(pendingReview));}catch(e){console.warn('save failed',e)}
}

let events=load(KEYS.events,[]);
let library=load(KEYS.library,[]);
let triggers=load(KEYS.triggers,[]);
let recent=load(KEYS.recent,[]);
let pendingReview=load(KEYS.review,[]);

// ---------- poster placeholder image generator (for seed data "original photos") ----------
function posterSVG(emoji,title,sub,tint){
  const t=esc(title).slice(0,18), s=esc(sub||'').slice(0,22);
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="480" height="620">
    <rect width="480" height="620" fill="${tint}"/>
    <rect x="0" y="0" width="480" height="46" fill="rgba(21,27,61,.08)"/>
    <text x="20" y="30" font-family="Arial" font-size="18" fill="#151B3D" font-weight="bold">9:41</text>
    <text x="240" y="330" text-anchor="middle" font-size="120">${emoji}</text>
    <text x="240" y="420" text-anchor="middle" font-family="Arial" font-size="26" fill="#151B3D" font-weight="bold">${t}</text>
    <text x="240" y="452" text-anchor="middle" font-family="Arial" font-size="16" fill="#5b5468">${s}</text>
  </svg>`;
  return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);
}

const H=3600000, D=86400000, NOW0=Date.now();
if(!events.length){
  events=[
    {id:'hackathon',date:'2026-09-20',time:'08:00–21:30',title:'AI VIBE CODING 해커톤',location:'AWS 역삼 센터필드',source:'기본 일정',image:'assets/hackathon.jpg'},
    {id:'gym-pt',date:'2026-09-22',time:'19:00',title:'헬스장 PT 예약 확인',location:'월드짐 강남점',source:'Snaptok AI',image:posterSVG('🏋️','PT 예약 확인','월드짐 강남점 · 19:00','#E1F3E6')},
    {id:'seminar-review',date:'2026-09-24',time:'시간 미정',title:'전공 세미나 안내',location:'장소 확인 필요',source:'Snaptok AI(사용자 확인)',image:posterSVG('📢','전공 세미나 안내','날짜만 확인, 장소 미정','#F6E4F4')},
    {id:'ideathon-deadline',date:'2026-09-27',time:'18:00',title:'AI 서비스 아이디어톤 신청 마감',location:'온라인',source:'Snaptok AI',image:posterSVG('🏆','아이디어톤 신청마감','9/27 18:00 · 온라인','#E3ECFF')},
    {id:'ideathon-final',date:'2026-09-29',time:'14:00',title:'아이디어톤 본선 발표',location:'온라인',source:'Snaptok AI',image:posterSVG('🎤','본선 발표','9/29 14:00 · 온라인','#FFE0E0')},
    {id:'study-group',date:'2026-09-21',time:'20:00',title:'알고리즘 스터디 모임',location:'학교 도서관 401호',source:'Snaptok AI',image:posterSVG('📚','스터디 모임','도서관 401호 · 20:00','#E1F3E6')},
    {id:'dentist',date:'2026-09-23',time:'15:30',title:'치과 예약',location:'서울역삼치과',source:'Snaptok AI',image:posterSVG('🦷','치과 예약','서울역삼치과 · 15:30','#DCEFFB')},
    {id:'friend-bday',date:'2026-09-25',time:'19:00',title:'재현이 생일 저녁 약속',location:'성수 오마카세',source:'Snaptok AI',image:posterSVG('🎂','생일 저녁 약속','성수 오마카세 · 19:00','#FFE1EC')},
    {id:'midterm',date:'2026-09-30',time:'09:00',title:'전공 중간고사',location:'공학관 302호',source:'Snaptok AI',image:posterSVG('📝','전공 중간고사','공학관 302호 · 09:00','#EDE6FB')},
  ];
}
if(!library.length){
  library=[
    {id:'seed-food-seongsu',title:'성수 생면 파스타',category:'맛집',place:'성수',note:'성수 방문 시 다시 보여주기',thumb:'🍝',image:posterSVG('🍝','성수 생면 파스타','성수 방문 시 다시 보여주기','#FFE3D6'),source:'스크린샷',confidence:.94,createdAt:NOW0-5*H,geoType:'specific',lat:37.5446,lng:127.0559,area:'성수'},
    {id:'seed-food-yeonnam',title:'연남동 파스타집',category:'맛집',place:'연남동',note:'연남동 갈 때 들르기',thumb:'🍝',image:posterSVG('🍝','연남동 파스타집','연남동 갈 때 들르기','#FFE3D6'),source:'스크린샷',confidence:.9,createdAt:NOW0-6*H,geoType:'specific',lat:37.5663,lng:126.9254,area:'연남동'},
    {id:'seed-food-yeoksam',title:'역삼 생면 파스타',category:'맛집',place:'역삼',note:'회사 근처 점심 후보',thumb:'🍝',image:posterSVG('🍝','역삼 생면 파스타','회사 근처 점심 후보','#FFE3D6'),source:'스크린샷',confidence:.9,createdAt:NOW0-7*H,geoType:'specific',lat:37.5015,lng:127.0380,area:'역삼'},
    {id:'seed-coupon-oliveyoung',title:'올리브영 세일 15% 쿠폰',category:'쿠폰',place:'',note:'코드 WELCOME15 · 사용기한 9/23',thumb:'🎟️',image:posterSVG('🎟️','올리브영 15% 쿠폰','코드 WELCOME15','#FFEBD0'),source:'카카오톡 공유',confidence:.93,createdAt:NOW0-1*D},
    {id:'seed-trip-huinyeoul',title:'흰여울문화마을',category:'여행지',place:'부산 영도',note:'부산 여행 후보',thumb:'🌊',image:posterSVG('🌊','흰여울문화마을','부산 영도 · 여행 후보','#DCEFFB'),source:'스크린샷',confidence:.92,createdAt:NOW0-1*D-3*H},
    {id:'seed-expo-media',title:'서울 미디어아트 전시',category:'전시회',place:'성수',note:'주말 관람 후보',thumb:'🖼️',image:posterSVG('🖼️','미디어아트 전시','성수 · 주말 관람 후보','#F6E4F4'),source:'스크린샷',confidence:.9,createdAt:NOW0-2*D},
    {id:'seed-fashion-jacket',title:'가을 바람막이 후드집업',category:'패션',place:'무신사',note:'쇼핑 관심 상품',thumb:'🧥',image:posterSVG('🧥','가을 바람막이','무신사 · 쇼핑 관심 상품','#EDE6FB'),source:'스크린샷',confidence:.9,createdAt:NOW0-2*D-4*H},
    {id:'seed-birthday-roommate',title:'룸메이트 생일 선물 후보',category:'생일',place:'',note:'다이슨 드라이기 사고 싶어함',thumb:'🎁',image:posterSVG('🎁','생일 선물 후보','다이슨 드라이기','#FFE1EC'),source:'카카오톡 공유',confidence:.88,createdAt:NOW0-3*D},
    {id:'seed-movie-interstellar',title:'인터스텔라 재개봉',category:'영화',place:'',note:'친구랑 같이 보러 가기로 함',thumb:'🎬',image:posterSVG('🎬','인터스텔라 재개봉','친구랑 보러 가기로 함','#E3E0FA'),source:'스크린샷',confidence:.87,createdAt:NOW0-3*D-6*H},
    {id:'seed-concert-day6',title:'데이식스 전국투어 티켓 오픈 안내',category:'콘서트',place:'',note:'티켓팅 날짜 다시 확인 필요',thumb:'🎤',image:posterSVG('🎤','데이식스 투어','티켓팅 날짜 확인 필요','#FFE0E0'),source:'스크린샷',confidence:.72,createdAt:NOW0-4*D},
    {id:'seed-study-algo',title:'알고리즘 스터디 정리노트',category:'공부',place:'',note:'동적계획법 파트 정리',thumb:'📚',image:posterSVG('📚','알고리즘 정리노트','동적계획법 파트','#E1F3E6'),source:'사진첩',confidence:.9,createdAt:NOW0-4*D-5*H},
    {id:'seed-trip-kyoto',title:'교토 벚꽃 여행 후보 스팟',category:'여행지',place:'교토',note:'내년 4월 여행 후보 · 저장만',thumb:'✈️',image:posterSVG('✈️','교토 벚꽃 여행','내년 4월 여행 후보','#DCEFFB'),source:'스크린샷',confidence:.85,createdAt:NOW0-5*D},
  ];
}
if(!recent.length){
  recent=[
    {id:'r-seed-1',kind:'event',refId:'ideathon-deadline',label:'캘린더 등록 · AI 서비스 아이디어톤 신청 마감',detail:'9/27 18:00',ts:NOW0-2*H,image:posterSVG('🏆','아이디어톤 신청마감','9/27 18:00','#E3ECFF')},
    {id:'r-seed-2',kind:'library',refId:'seed-coupon-oliveyoung',label:'보관함 저장 · 올리브영 세일 15% 쿠폰',detail:'쿠폰 · 사용기한 9/23',ts:NOW0-1*D,image:posterSVG('🎟️','올리브영 15%','사용기한 9/23','#FFEBD0')},
    {id:'r-seed-3',kind:'event',refId:'seminar-review',label:'캘린더 등록 · 전공 세미나 안내',detail:'날짜만 확실해 사용자 확인 후 등록',ts:NOW0-1*D-2*H,image:posterSVG('📢','전공 세미나','사용자 확인 후 등록','#F6E4F4')},
    {id:'r-seed-4',kind:'library',refId:'seed-food-seongsu',label:'보관함 저장 · 성수 생면 파스타',detail:'맛집 · 성수',ts:NOW0-5*H,image:posterSVG('🍝','성수 파스타','성수','#FFE3D6')},
    {id:'r-seed-5',kind:'library',refId:'seed-concert-day6',label:'보관함 저장 · 데이식스 콘서트',detail:'확신도 낮아 확인 필요로 표시',ts:NOW0-4*D,image:posterSVG('🎤','데이식스 투어','확인 필요','#FFE0E0')},
  ];
}
// (시드 trigger 제거: 위치 감시는 geoTargets(=보관함 geoType 항목) 기준으로 동작)
saveAll();

// ---------- nav ----------
function page(id){
  $$('.page').forEach(p=>p.classList.toggle('active',p.id===id));
  $$('nav.tabbar button[data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===id));
  closeSheet();
  if(id==='page-calendar')renderCalendar();
  if(id==='page-library')renderLibrary();
  if(id==='page-activity')renderActivity();
  if(id==='page-report')renderReport();
  if(id==='page-today')renderToday();
}
$$('nav.tabbar button[data-page]').forEach(b=>b.onclick=()=>page(b.dataset.page));
$('#fab').onclick=()=>openAddMenu();
$('#goCalendar').onclick=()=>{selectedDate=null;page('page-calendar')};
$('#calBack').onclick=()=>page('page-today');
$('#goActivity').onclick=()=>page('page-activity');
$('#wrappedPromo').onclick=()=>page('page-report');

// ---------- sheet / toast ----------
const grab='<div class="grab"></div>';
function setSheet(html){$('#sheet').innerHTML=html;$('#sheetOverlay').classList.add('show')}
function closeSheet(){$('#sheetOverlay').classList.remove('show')}
$('#sheetOverlay').addEventListener('click',e=>{if(e.target.id==='sheetOverlay')closeSheet()});

function toast(title,body,undoFn){
  $('#toastTitle').textContent=title; $('#toastBody').textContent=body||'';
  const u=$('#toastUndo');
  if(undoFn){u.style.display='inline-block';u.onclick=()=>{undoFn();$('#toast').classList.remove('show')}}
  else{u.style.display='none'}
  $('#toast').classList.add('show');
  clearTimeout(window.__t);window.__t=setTimeout(()=>$('#toast').classList.remove('show'),5200);
}
function push(title,body){
  $('#pushTitle').textContent=title;$('#pushBody').textContent=body||'';
  $('#push').classList.add('show');
  clearTimeout(window.__p);window.__p=setTimeout(()=>$('#push').classList.remove('show'),5200);
}

// ---------- greeting ----------
(function greet(){
  const h=new Date().getHours();
  $('#greetLine').textContent = h<11? '좋은 아침이에요' : h<18? '좋은 오후예요' : '좋은 저녁이에요';
})();

// ---------- time helper ----------
function timeAgo(ts){
  if(!ts)return'';
  const diff=Math.max(0,Date.now()-ts), m=Math.floor(diff/60000);
  if(m<1)return'방금';
  if(m<60)return m+'분 전';
  const h=Math.floor(m/60); if(h<24)return h+'시간 전';
  return Math.floor(h/24)+'일 전';
}

// ---------- recent activity / recover ----------
function logRecent(entry){
  recent=[{...entry,id:'r'+Date.now()+Math.random().toString(16).slice(2),ts:Date.now()},...recent].slice(0,60);
  saveAll(); renderToday();
}
function undoRecent(logId){
  const entry=recent.find(r=>r.id===logId); if(!entry)return;
  if(entry.kind==='event') events=events.filter(e=>e.id!==entry.refId);
  if(entry.kind==='library') library=library.filter(l=>l.id!==entry.refId);
  recent=recent.filter(r=>r.id!==logId);
  saveAll(); renderToday(); renderCalendar(); renderLibrary(); renderActivity();
  toast('되돌렸어요',entry.label);
}
function renderRecentRow(r){
  return `<div class="cal-item"><img class="thumb-mini" src="${r.image||''}" onerror="this.style.display='none'"><div><strong>${esc(r.label)}</strong><small>${esc(r.detail||'')} · ${timeAgo(r.ts)}</small></div><button class="undo-mini" data-undo="${r.id}">되돌리기</button></div>`;
}
function renderToday(){
  $('#triggerCount').textContent=geoTargets().filter(t=>t.geo_enabled!==false && !t.used).length+'개 등록';
  const prev=$('#recentPreview');
  prev.innerHTML = recent.length ? recent.slice(0,3).map(renderRecentRow).join('') : '<div class="empty"><h2>아직 활동이 없어요</h2><p>스크린샷을 맡기면 여기 기록돼요.</p></div>';
  prev.querySelectorAll('[data-undo]').forEach(b=>b.onclick=()=>undoRecent(b.dataset.undo));

  // today's / upcoming events
  const todays=events.filter(e=>e.date===TODAY);
  const upcoming=events.filter(e=>e.date>TODAY).sort((a,b)=>a.date.localeCompare(b.date));
  const show = todays.length? todays : upcoming.slice(0,1);
  $('#todayEvents').innerHTML = show.length? show.map(eventCardHtml).join('') + (todays.length===0&&upcoming.length? `<p style="font-size:11px;color:var(--muted);margin:2px 2px 0">오늘은 일정이 없어요 · 다음 일정을 보여드려요</p>`:'') : '<div class="empty"><h2>오늘은 일정이 없어요</h2><p>여유로운 하루 보내세요.</p></div>';
  $$('#todayEvents [data-ev]').forEach(b=>b.onclick=()=>openEventDetail(events.find(e=>e.id===b.dataset.ev)));

  renderLocationCard();
  renderReviewQueue();
}
function eventCardHtml(e){
  const d=new Date(e.date+'T00:00:00');
  const curY=new Date().getFullYear();
  const yr=(e.date&&d.getFullYear()!==curY)? d.getFullYear()+'. ' : '';
  return `<div class="event-card" data-ev="${e.id}"><div class="datebadge"><strong>${d.getDate()}</strong><span>${String(d.getMonth()+1).padStart(2,'0')}/${WD[d.getDay()]}</span></div><div class="ev-meta"><strong>${esc(e.title)}</strong><small>${yr}${esc(e.time||'시간 미정')}${e.location?' · '+esc(e.location):''}</small></div><span class="chev">›</span></div>`;
}

// ---------- review queue (uncertain items left unresolved) ----------
function renderReviewQueue(){
  const head=$('#reviewHead'), q=$('#reviewQueue');
  if(!pendingReview.length){head.style.display='none';q.innerHTML='';return}
  head.style.display='flex';
  $('#reviewCount').textContent=pendingReview.length+'건';
  q.innerHTML=pendingReview.map(r=>`<div class="needsreview-card" data-rid="${r.id}"><img src="${r.dataUrl||r.image||''}"><div><strong>${esc(r.title)}</strong><small>확인 필요 · ${esc(r.note||'')}</small></div></div>`).join('');
  q.querySelectorAll('[data-rid]').forEach(el=>el.onclick=()=>resolvePending(pendingReview.find(r=>r.id===el.dataset.rid)));
}
function resolvePending(r){
  if(!r)return;
  setSheet(grab+`<span class="chip">확인 필요</span><h2>${esc(r.title)}</h2>
  <img class="imgpreview" src="${r.dataUrl||r.image||''}" style="max-height:200px;object-fit:contain">
  <p class="copy">${esc(r.note||'AI가 판단을 확신하지 못했어요.')}</p>
  <div class="decision"><button class="a" id="rvSchedule">일정으로</button><button class="b" id="rvMemory">보관만</button></div>
  <button class="secondary" id="rvDelete">삭제</button>`);
  $('#rvSchedule').onclick=()=>{
    if(!r.date){ toast('날짜를 확인하지 못했어요','이 항목은 날짜가 없어 일정으로 저장할 수 없어요. 보관만 하거나 삭제해주세요.'); return; }
    addEventAuto({date:r.date,time:r.time||'시간 미정',title:r.title,location:r.place||'',image:r.dataUrl},'Snaptok AI(사용자 확인)');
    pendingReview=pendingReview.filter(x=>x.id!==r.id); saveAll(); closeSheet(); renderToday(); toast('일정으로 저장했어요',r.title);
  };
  $('#rvMemory').onclick=()=>{
    addLibraryAuto({title:r.title,category:r.category||'기타',place:r.place,note:r.note,confidence:r.confidence,image:r.dataUrl},'Snaptok AI(사용자 확인)');
    pendingReview=pendingReview.filter(x=>x.id!==r.id); saveAll(); closeSheet(); renderToday(); toast('보관함에 저장했어요',r.title);
  };
  $('#rvDelete').onclick=()=>{
    pendingReview=pendingReview.filter(x=>x.id!==r.id); saveAll(); closeSheet(); renderToday(); toast('삭제했어요',r.title);
  };
}

// ---------- duplicate check ----------
function normTitle(s){return String(s||'').toLowerCase().replace(/[\s\u3000·,\.\-\_\/\(\)!?~]+/g,'')}
function bigrams(s){const out=new Set();for(let i=0;i<s.length-1;i++)out.add(s.slice(i,i+2));return out}
function similarity(a,b){
  const A=bigrams(normTitle(a)), B=bigrams(normTitle(b));
  if(!A.size||!B.size)return normTitle(a)===normTitle(b)?1:0;
  let inter=0; A.forEach(g=>{if(B.has(g))inter++});
  return (2*inter)/(A.size+B.size);
}
function findDuplicateEvent(candidate){return events.find(e=>e.date===candidate.date && similarity(e.title,candidate.title)>=0.55)}
function findDuplicateLibrary(candidate){return library.find(l=>l.category===candidate.category && similarity(l.title,candidate.title)>=0.55)}

// ---------- add event / library (core actions) ----------
function addEventAuto(ev,sourceLabel){
  const dup=findDuplicateEvent(ev);
  if(dup) return {status:'dup',existing:dup};
  const record={...ev,id:ev.id||('ai-'+Date.now()+Math.random().toString(16).slice(2)),source:sourceLabel||'Snaptok AI'};
  events=[record,...events]; saveAll();
  logRecent({kind:'event',refId:record.id,label:'캘린더 등록 · '+record.title,detail:(record.date||'')+' '+(record.time||''),image:record.image});
  return {status:'added',record};
}
function addLibraryAuto(item,sourceLabel){
  const dup=findDuplicateLibrary(item);
  if(dup) return {status:'dup',existing:dup};
  const record={id:'ai-'+Date.now()+Math.random().toString(16).slice(2),title:item.title,category:item.category||'기타',place:item.place||'',note:item.note||'',thumb:CAT_EMOJI[item.category]||'📁',image:item.image||'',source:sourceLabel||'Snaptok AI',confidence:item.confidence??0.7,createdAt:Date.now(),
    geoType:item.geoType||undefined,lat:item.lat??undefined,lng:item.lng??undefined,radius:item.radius??undefined,area:item.area||undefined,brand:item.brand||undefined,branches:item.branches||undefined,expiry:item.expiry||undefined,used:item.used||false};
  library=[record,...library]; saveAll();
  logRecent({kind:'library',refId:record.id,label:'보관함 저장 · '+record.title,detail:record.category+(record.place?' · '+record.place:''),image:record.image});
  return {status:'added',record};
}

// ---------- event detail (with original photo) ----------
function openEventDetail(ev){
  if(!ev)return;
  const isAi=ev.source&&ev.source.includes('AI');
  setSheet(grab+`<span class="chip ${isAi?'navy':'muted'}">${esc(ev.source||'일정')}</span>
  <h2>${esc(ev.title)}</h2>
  ${ev.image?`<img class="imgpreview" src="${ev.image}" style="max-height:260px;object-fit:contain">`:'<div class="empty" style="margin:10px 0"><h2>원본 이미지가 없어요</h2><p>직접 추가한 일정이에요.</p></div>'}
  <p class="copy">📅 ${esc(ev.date)} · ${esc(ev.time||'시간 미정')}</p>
  <p class="copy">📍 ${esc(ev.location||'장소 정보 없음')}</p>
  ${isAi?`<button class="secondary" id="undoEvent">되돌리기</button>`:''}
  <button class="secondary" id="closeEventDetail">닫기</button>`);
  $('#closeEventDetail').onclick=closeSheet;
  const ub=$('#undoEvent'); if(ub)ub.onclick=()=>{
    const log=recent.find(r=>r.kind==='event'&&r.refId===ev.id);
    events=events.filter(e=>e.id!==ev.id);
    if(log) recent=recent.filter(r=>r.id!==log.id);
    saveAll(); closeSheet(); renderCalendar(); renderToday(); toast('되돌렸어요',ev.title);
  };
}

// ---------- calendar render + date filter ----------
let selectedDate=null;
function renderCalendar(){
  const grid=$('#monthGrid'); const first=new Date(2026,8,1).getDay();
  const wdRow=WD.map(w=>`<div class="wd">${w}</div>`).join('');
  const cells=[]; for(let i=0;i<first;i++)cells.push('<button class="date muted" disabled></button>');
  for(let d=1;d<=30;d++){
    const ds=`2026-09-${String(d).padStart(2,'0')}`;
    const has=events.some(e=>e.date===ds);
    const cls=['date']; if(d===20)cls.push('today'); if(has)cls.push('has-event'); if(selectedDate===ds)cls.push('selected');
    cells.push(`<button class="${cls.join(' ')}" data-date="${ds}">${d}</button>`);
  }
  grid.innerHTML=wdRow+cells.join('');
  $$('#monthGrid [data-date]').forEach(b=>b.onclick=()=>{selectedDate=(selectedDate===b.dataset.date)?null:b.dataset.date; renderCalendar()});
  $('#eventCount').textContent=events.length+'개';

  const list=selectedDate? events.filter(e=>e.date===selectedDate) : events.slice().sort((a,b)=>String(a.date).localeCompare(String(b.date)));
  if(selectedDate){
    const d=new Date(selectedDate+'T00:00:00');
    $('#filterLabel').textContent=`${d.getMonth()+1}월 ${d.getDate()}일 (${WD[d.getDay()]}) · ${list.length}개`;
    $('#clearFilter').style.display='inline-block';
  }else{
    $('#filterLabel').textContent='전체 일정';
    $('#clearFilter').style.display='none';
  }
  $('#eventList').innerHTML = list.length? list.map(e=>
    `<div class="cal-item" data-ev="${e.id}"><span class="dot"></span><div><strong>${esc(e.title)}</strong><small>${esc((e.date||'').replace('2026-','').replace('-','/'))} · ${esc(e.time||'시간 미정')}${e.location?' · '+esc(e.location):''}</small></div><span class="ai-mark">${e.source&&e.source.includes('AI')?'AI 등록':'일정'}</span></div>`
  ).join('') : '<div class="empty"><h2>이 날은 일정이 없어요</h2><p>다른 날짜를 선택해보세요.</p></div>';
  $$('#eventList [data-ev]').forEach(b=>b.onclick=()=>openEventDetail(events.find(e=>e.id===b.dataset.ev)));
}
$('#clearFilter').onclick=()=>{selectedDate=null;renderCalendar()};

// ---------- library render ----------
let libTab='전체', libSearch='';
function renderLibraryTabs(){
  $('#libraryTabs').innerHTML=['전체',...CATEGORIES].map(c=>`<button data-tab="${c}" class="${c===libTab?'selected':''}">${c}</button>`).join('');
  $$('#libraryTabs [data-tab]').forEach(b=>b.onclick=()=>{libTab=b.dataset.tab;renderLibrary()});
}
function renderLibrary(){
  renderLibraryTabs();
  const list=library.filter(l=>(libTab==='전체'||l.category===libTab)&&[l.title,l.place,l.note].join(' ').toLowerCase().includes(libSearch.toLowerCase()));
  $('#libraryCount').textContent=list.length+'개의 기억 · 최근 저장순';
  $('#libraryGrid').innerHTML=list.length?list.map(l=>`<button class="lib-card" data-id="${l.id}"><div class="thumb">${l.image?`<img src="${l.image}">`:(l.thumb||CAT_EMOJI[l.category]||'📁')}</div><div class="meta"><strong>${esc(l.title)}</strong><small>${esc(l.category)}${l.place?' · '+esc(l.place):''}</small></div></button>`).join(''):'<div class="empty"><h2>아직 저장된 정보가 없어요</h2><p>스크린샷·사진을 맡기면 자동으로 정리돼요.</p></div>';
  $$('#libraryGrid [data-id]').forEach(b=>b.onclick=()=>openLibraryDetail(library.find(x=>x.id===b.dataset.id)));
}
$('#librarySearch').oninput=e=>{libSearch=e.target.value;renderLibrary()};

function openLibraryDetail(item){
  if(!item)return;
  const activeTrigger=triggers.find(t=>t.itemId===item.id && t.active);
  setSheet(grab+`<span class="chip navy">${esc(item.category)} · ${esc(item.source||'')}</span>
  <h2>${esc(item.title)}</h2>
  ${item.image?`<img class="imgpreview" src="${item.image}" style="max-height:220px;object-fit:contain">`:`<div style="font-size:44px;text-align:center;margin:14px 0">${item.thumb||CAT_EMOJI[item.category]||'📁'}</div>`}
  <p class="copy">${esc(item.place||'장소 정보 없음')}</p>
  <p class="copy">${esc(item.note||'추가 메모 없음')}</p>
  ${activeTrigger?`<div class="chip navy" style="display:block;padding:9px 11px">📍 이 위치(반경 ${activeTrigger.radius}m) 근처에 오면 다시 알려드려요.</div>`:''}
  <button class="secondary" id="toggleTrigger">${activeTrigger?'위치 알림 끄기':'📍 여기서 다시 알려주기'}</button>
  ${activeTrigger?`<button class="ghost-btn" id="testTrigger" style="width:100%;margin-top:8px">지금 알림 미리 보기(테스트)</button>`:''}
  ${item.geoType==='brand'?`<button class="secondary" id="couponUsed" style="background:${geoState.usedCoupons.includes(item.id)?'#EFECFB':'#F1EEF8'}">${geoState.usedCoupons.includes(item.id)?'✓ 사용 완료':'사용했어요'}</button>`:''}
  <button class="secondary" id="closeDetail">닫기</button>`);
  $('#closeDetail').onclick=closeSheet;
  $('#toggleTrigger').onclick=()=>activeTrigger?disableTrigger(item):enableTrigger(item);
  const tb=$('#testTrigger'); if(tb)tb.onclick=()=>fireTrigger(activeTrigger);
  const cu=$('#couponUsed'); if(cu)cu.onclick=()=>{
    if(!geoState.usedCoupons.includes(item.id)){geoState.usedCoupons=[...geoState.usedCoupons,item.id]; geoSave();}
    toast('사용 완료로 표시했어요',item.title); openLibraryDetail(item);
  };
}

// ---------- activity (full list) ----------
function renderActivity(){
  $('#activityList').innerHTML = recent.length? recent.map(renderRecentRow).join('') : '<div class="empty"><h2>아직 활동이 없어요</h2><p>스크린샷을 맡기면 여기 기록돼요.</p></div>';
  $$('#activityList [data-undo]').forEach(b=>b.onclick=()=>undoRecent(b.dataset.undo));
}

// ---------- location: haversine + live card ----------
function haversine(lat1,lon1,lat2,lon2){
  const R=6371000,toRad=d=>d*Math.PI/180;
  const dLat=toRad(lat2-lat1), dLon=toRad(lon2-lon1);
  const a=Math.sin(dLat/2)**2+Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLon/2)**2;
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}
let lastPosition=null, watcherId=null, permState='unknown';
function fmtDist(m){return m<1000? Math.round(m)+'m' : (m/1000).toFixed(1)+'km'}
function pinPos(id){ // deterministic pseudo-position for decorative map
  let h=0; for(const c of id) h=(h*31+c.charCodeAt(0))%997;
  return {left: 18+(h%64)+'%', top: 20+((h*7)%55)+'%'};
}
function renderLocationCard(){
  const box=$('#locationCard');
  const activeTriggers=triggers.filter(t=>t.active);
  if(permState==='denied'){
    box.innerHTML=`<div class="locdenied"><strong>📍 위치 권한이 필요해요</strong><p>브라우저 설정에서 위치 접근을 허용해주세요.</p><button id="locRetry">다시 시도</button></div>`;
    $('#locRetry').onclick=requestLocation;
    return;
  }
  if(!activeTriggers.length){
    box.innerHTML=`<div class="card" style="text-align:center;padding:22px 16px"><p style="font-size:12.5px;color:var(--muted);margin:0 0 10px">보관함 항목에서 "여기서 다시 알려주기"를 켜면, 실시간 위치로 근처 도착을 알려드려요.</p><button class="ghost-btn" id="goLibFromMap">보관함 보러가기</button></div>`;
    const g=$('#goLibFromMap'); if(g)g.onclick=()=>page('page-library');
    return;
  }
  let nearest=null, nearestDist=Infinity;
  if(lastPosition){
    activeTriggers.forEach(t=>{const d=haversine(lastPosition.lat,lastPosition.lng,t.lat,t.lng); if(d<nearestDist){nearestDist=d;nearest=t}});
  }
  const pins=activeTriggers.map(t=>{const p=pinPos(t.id); return `<div class="pin" data-trig="${t.id}" style="left:${p.left};top:${p.top}">📍</div>`}).join('');
  box.innerHTML=`<div class="map-card">${pins}
    <span class="stationchip">${lastPosition?'📡 현재 위치':'📍 역삼역'}</span>
    ${nearest?`<span class="distchip">${esc(nearest.title)} · ${fmtDist(nearestDist)}</span>`:(permState!=='granted'?`<span class="distchip" id="locAsk" style="cursor:pointer">위치 켜기</span>`:'')}
  </div>
  ${nearest && nearestDist<=nearest.radius ? `<div class="card" style="margin-top:10px;background:#FFF3D6"><strong style="font-size:13px;color:#8A6100">🔔 지금 근처예요!</strong><p style="font-size:12px;color:#8A6100;margin:6px 0 0">${esc(nearest.title)}</p></div>`:''}
  <div class="card" style="margin-top:10px" id="quickTestWrap"></div>`;
  $$('.map-card [data-trig]').forEach(p=>p.onclick=()=>{const t=triggers.find(x=>x.id===p.dataset.trig); const item=library.find(l=>l.id===t.itemId); if(item)openLibraryDetail(item)});
  const ask=$('#locAsk'); if(ask)ask.onclick=requestLocation;
  const qt=$('#quickTestWrap');
  if(nearest){
    qt.innerHTML=`<div class="row" style="justify-content:space-between"><small style="font-size:11.5px;color:var(--muted)">${lastPosition?'실시간 GPS 기준 거리예요':'위치를 켜면 실시간 거리로 바뀌어요'}</small><button class="ghost-btn" id="quickFire">지금 도착 알림 테스트</button></div>`;
    $('#quickFire').onclick=()=>fireTrigger(nearest);
  } else qt.remove();
}
function requestLocation(){
  if(!navigator.geolocation){toast('위치 기능을 쓸 수 없어요','이 브라우저는 위치 정보를 지원하지 않아요.');return}
  navigator.geolocation.getCurrentPosition(pos=>{
    permState='granted'; lastPosition={lat:pos.coords.latitude,lng:pos.coords.longitude};
    ensureWatcher(); renderLocationCard();
  },err=>{
    if(err.code===1){permState='denied'} // 실제 거부일 때만 "권한 필요" 카드로 전환
    else{toast('위치를 확인하지 못했어요','잠시 후 다시 시도해주세요.')}
    renderLocationCard();
  },{enableHighAccuracy:true,timeout:15000,maximumAge:30000});
}
function enableTrigger(item){
  if(!navigator.geolocation){toast('위치 기능을 쓸 수 없어요','이 브라우저는 위치 정보를 지원하지 않아요.');return}
  navigator.geolocation.getCurrentPosition(pos=>{
    permState='granted'; lastPosition={lat:pos.coords.latitude,lng:pos.coords.longitude};
    const t={id:'trig-'+Date.now(),itemId:item.id,title:item.title,lat:pos.coords.latitude,lng:pos.coords.longitude,radius:300,active:true,fired:false};
    triggers=[...triggers.filter(x=>x.itemId!==item.id),t]; saveAll();
    toast('위치 알림을 켰어요',item.title+' · 반경 300m');
    ensureWatcher(); openLibraryDetail(item); renderToday();
  },err=>{
    if(err.code===1){permState='denied';toast('위치 권한이 필요해요','브라우저 설정에서 위치 접근을 허용해주세요.')}
    else{toast('위치를 확인하지 못했어요','잠시 후 다시 시도해주세요.')}
    renderLocationCard();
  },{enableHighAccuracy:true,timeout:15000,maximumAge:30000});
}
function disableTrigger(item){
  triggers=triggers.map(t=>t.itemId===item.id?{...t,active:false}:t); saveAll();
  toast('위치 알림을 껐어요',item.title);
  openLibraryDetail(item); renderToday();
}
function fireTrigger(t){
  if(!t)return;
  push('Snaptok · 근처에서 다시 꺼냈어요',t.title+' 근처예요.');
  logRecent({kind:'noop',refId:'noop-'+Date.now(),label:'위치 알림 · '+t.title,detail:'근처 도착 알림',image:''});
}
function ensureWatcher(){
  if(watcherId!==null || !navigator.geolocation)return;
  watcherId=navigator.geolocation.watchPosition(pos=>{
    lastPosition={lat:pos.coords.latitude,lng:pos.coords.longitude};
    if($('#page-today').classList.contains('active')) renderLocationCard();
    triggers.forEach(t=>{
      if(!t.active||t.fired)return;
      const d=haversine(pos.coords.latitude,pos.coords.longitude,t.lat,t.lng);
      if(d<=t.radius){t.fired=true;saveAll();fireTrigger(t)}
    });
  },()=>{},{enableHighAccuracy:false,maximumAge:60000});
}
// detect existing permission without prompting
if(navigator.permissions && navigator.permissions.query){
  navigator.permissions.query({name:'geolocation'}).then(res=>{
    permState=res.state;
    if(res.state==='granted'){requestLocation()} else renderLocationCard();
    res.onchange=()=>{permState=res.state; renderLocationCard()};
  }).catch(()=>{renderLocationCard()});
}

// ================= 지오펜스 위치 알림 =================
// 위치 좌표 자체는 저장/전송하지 않는다. 감시 상태(진입/체류/거리)는 메모리에만 두고,
// localStorage에는 알림 기록과 쿨다운/일일 카운트/차단 목록만 남긴다.
const GEO_KEYS={log:'snaptok_geo_log_v1',state:'snaptok_geo_state_v1'};
function geoLoad(key,fb){try{const v=JSON.parse(localStorage.getItem(key));return v&&typeof v==='object'?v:fb}catch{return fb}}
let geoLog=geoLoad(GEO_KEYS.log,[]);
let geoState=geoLoad(GEO_KEYS.state,{lastNotified:{},dailyCount:0,dailyDate:'',doNotAsk:[],usedCoupons:[],demoMode:true,mode:'sim'});
function geoSave(){try{localStorage.setItem(GEO_KEYS.log,JSON.stringify(geoLog.slice(0,40)));localStorage.setItem(GEO_KEYS.state,JSON.stringify(geoState))}catch(e){console.warn('geo save failed',e)}}

// 프리셋 좌표는 시연용 근사값이며 실제 매장/장소 위치와 다를 수 있음
const GEO_PRESETS={
  '발표장':{lat:37.5003,lng:127.0366},
  '연남동':{lat:37.5663,lng:126.9254},
  '성수':{lat:37.5446,lng:127.0559},
  '역삼 스타벅스 앞':{lat:37.5007,lng:127.0359},
  '멀리':{lat:37.5547,lng:126.9707},
};
let virtualPos={...GEO_PRESETS['발표장']};

function geoTargets(){ return library.filter(l=>l.geoType); }
function geoDistance(pos,t){
  if(t.geoType==='brand'){let min=Infinity; t.branches.forEach(b=>{const d=haversine(pos.lat,pos.lng,b.lat,b.lng); if(d<min)min=d}); return min;}
  return haversine(pos.lat,pos.lng,t.lat,t.lng);
}
function geoRadius(t){return t.geoType==='brand'?150:(t.geoType==='area'?700:150)}
function todayKey(){return new Date().toDateString()}
function ensureDailyReset(){ if(geoState.dailyDate!==todayKey()){geoState.dailyDate=todayKey(); geoState.dailyCount=0; geoSave()} }
function inTimeWindow(cat){
  if(geoState.demoMode) return true;
  const h=new Date().getHours();
  if(cat==='맛집') return (h>=11&&h<14)||(h>=17&&h<21);
  return h>=9&&h<21; // 카페·쿠폰·그 외
}
function isCoolingDown(t){
  if(geoState.demoMode) return false;
  const last=geoState.lastNotified[t.id]; if(!last) return false;
  return (Date.now()-last) < 7*24*3600*1000;
}
function logGeo(name,result){ geoLog=[{ts:Date.now(),name,result},...geoLog].slice(0,40); geoSave(); renderGeoDebug(); }
function attemptNotify(t){
  ensureDailyReset();
  if(t.geoType==='brand'){
    if(geoState.usedCoupons.includes(t.id)){logGeo(t.title,'사용한 쿠폰'); return}
    if(t.expiry && t.expiry<TODAY){logGeo(t.title,'만료된 쿠폰'); return}
  }
  if(geoState.doNotAsk.includes(t.id)){logGeo(t.title,'다시 알리지 않기'); return}
  if(isCoolingDown(t)){logGeo(t.title,'쿨다운으로 생략'); return}
  if(geoState.dailyCount>=2){logGeo(t.title,'상한 초과'); return}
  if(!inTimeWindow(t.category)){logGeo(t.title,'시간대 밖'); return}
  geoState.lastNotified[t.id]=Date.now(); geoState.dailyCount++; geoSave();
  fireGeoNotification(t); logGeo(t.title,'알림');
}
function geoMessage(t){
  if(t.geoType==='brand'){
    const d=t.expiry? t.expiry.slice(5).replace('-','/') : '';
    return `근처에 ${t.title}가 있어요 · ${d}까지인 쿠폰이 남아 있어요`;
  }
  const sameArea=geoTargets().filter(x=>x.area && x.area===t.area && x!==t && x._status==='inside');
  if(sameArea.length) return `${t.area}에 저장해 둔 곳이 ${sameArea.length+1}개 있어요 · ${t.title} 외 ${sameArea.length}곳`;
  return `근처에 저장해 둔 ${t.title}이(가) 있어요 · ${t.category}`;
}
function fireGeoNotification(t){
  const msg=geoMessage(t);
  showGeoBanner(t,msg);
  if(typeof Notification!=='undefined' && Notification.permission==='granted' && document.hidden){
    try{ new Notification('Snaptok', {body:msg}); }catch(e){}
  }
}
function showGeoBanner(t,msg){
  const b=$('#geoBanner'); if(!b)return;
  b.innerHTML=`<img src="${t.image||''}" class="geo-thumb"><div class="geo-txt"><strong>Snaptok</strong><span>${esc(msg)}</span></div><button class="geo-x" id="geoDismiss">✕ 다시 알리지 않기</button>`;
  b.classList.add('show');
  b.onclick=(e)=>{
    if(e.target.id==='geoDismiss'){ e.stopPropagation(); geoState.doNotAsk=[...geoState.doNotAsk,t.id]; geoSave(); hideGeoBanner(); toast('다시 알리지 않을게요',t.title); return; }
    hideGeoBanner(); const item=library.find(l=>l.id===t.id); if(item)openLibraryDetail(item);
  };
  clearTimeout(window.__geoTimer); window.__geoTimer=setTimeout(hideGeoBanner,5000);
}
function hideGeoBanner(){ const b=$('#geoBanner'); if(b)b.classList.remove('show'); }

function geoTick(){
  const pos = geoState.mode==='sim' ? virtualPos : lastPosition;
  if(!pos) return;
  const now=Date.now(), dwellNeeded=geoState.demoMode?10:180;
  geoTargets().forEach(t=>{
    const d=geoDistance(pos,t), r=geoRadius(t);
    if(d<=r){
      if(t._status!=='inside'){
        if(!t._dwellStart) t._dwellStart=now;
        const dwelled=(now-t._dwellStart)/1000;
        t._status = dwelled>=dwellNeeded ? 'inside' : 'entering';
        if(t._status==='inside') attemptNotify(t);
      }
    } else if(d>r+30){ t._status='outside'; t._dwellStart=null; }
    t._dist=d;
  });
  renderGeoDebug();
}
setInterval(geoTick,1000);

function geoMoveTo(name){
  const target=GEO_PRESETS[name]; if(!target)return;
  const from={...virtualPos}; const steps=6; let i=0;
  clearInterval(window.__geoMoveTimer);
  window.__geoMoveTimer=setInterval(()=>{
    i++; virtualPos={lat:from.lat+(target.lat-from.lat)*i/steps, lng:from.lng+(target.lng-from.lng)*i/steps};
    if(i>=steps) clearInterval(window.__geoMoveTimer);
    renderGeoDebug();
  },250);
}

function statusLabel(t){
  if(t._status==='inside')return '체류 중';
  if(t._status==='entering')return `진입 · ${Math.max(0,Math.round((geoState.demoMode?10:180)-((Date.now()-(t._dwellStart||Date.now()))/1000)))}초 남음`;
  return '바깥';
}
function openGeoSettings(){
  setSheet(grab+`<span class="chip navy">지오펜스</span><h2>위치 알림 설정</h2>
  <p class="copy">저장해 둔 장소 근처에 머물면 Snaptok이 먼저 알려드려요. 위치는 기기 밖으로 전송되지 않아요.</p>
  <div class="field">모드<select id="geoModeSel"><option value="sim">위치 시뮬레이터(발표용)</option><option value="real">실제 위치</option></select></div>
  <div class="row" style="justify-content:space-between;margin:10px 2px">
    <span style="font-size:13px;font-weight:700;color:var(--navy)">데모 모드(체류 10초·쿨다운 무시)</span>
    <input type="checkbox" id="geoDemoChk">
  </div>
  <div id="geoSimBlock"></div>
  <div class="section-head"><strong>감시 중인 장소</strong><span></span></div>
  <div id="geoWatchList"></div>
  <div class="section-head"><strong>알림 기록</strong><button class="see-all" id="geoResetLog">기록 초기화</button></div>
  <div id="geoLogList"></div>
  <p class="foot-note">같은 정보는 7일 안에 다시 알리지 않고, 하루 최대 2개예요. 위치는 기기 밖으로 전송되지 않아요.</p>
  <button class="secondary" id="closeGeoSettings">닫기</button>`);
  $('#geoModeSel').value=geoState.mode;
  $('#geoDemoChk').checked=geoState.demoMode;
  $('#geoModeSel').onchange=e=>{geoState.mode=e.target.value; geoSave(); if(geoState.mode==='real')requestLocation(); renderGeoSimBlock()};
  $('#geoDemoChk').onchange=e=>{geoState.demoMode=e.target.checked; geoSave()};
  $('#geoResetLog').onclick=()=>{geoLog=[]; geoState.lastNotified={}; geoState.dailyCount=0; geoSave(); renderGeoDebug(); toast('알림 기록을 초기화했어요','')};
  $('#closeGeoSettings').onclick=closeSheet;
  renderGeoSimBlock(); renderGeoDebug();
}
function renderGeoSimBlock(){
  const el=$('#geoSimBlock'); if(!el)return;
  if(geoState.mode!=='sim'){el.innerHTML='';return}
  el.innerHTML=`<div class="row" style="flex-wrap:wrap;gap:8px;margin:10px 0">${Object.keys(GEO_PRESETS).map(k=>`<button class="ghost-btn" data-preset="${esc(k)}">${esc(k)}</button>`).join('')}</div>
  <p style="font-size:11px;color:var(--muted);margin:0 0 6px">웹 데모에서는 앱이 열려 있을 때만 위치를 확인해요. 실제 앱은 백그라운드에서도 동작해요.</p>`;
  $$('#geoSimBlock [data-preset]').forEach(b=>b.onclick=()=>geoMoveTo(b.dataset.preset));
}
function renderGeoDebug(){
  const wl=$('#geoWatchList'), ll=$('#geoLogList');
  const pos=geoState.mode==='sim'?virtualPos:(lastPosition||GEO_PRESETS['발표장']);
  if(wl){
    wl.innerHTML=geoTargets().map(t=>`<div class="cal-item"><span class="dot"></span><div><strong>${esc(t.title)}</strong><small>${t.geoType==='brand'?'브랜드':'특정 장소'} · ${fmtDist(t._dist??geoDistance(pos,t))} · ${statusLabel(t)}</small></div></div>`).join('')||'<p style="font-size:12px;color:var(--muted)">감시 대상이 없어요.</p>';
  }
  if(ll){
    ll.innerHTML=geoLog.length? geoLog.slice(0,10).map(g=>`<div class="cal-item"><span class="dot" style="background:${g.result==='알림'?'var(--coral)':'#C9C6E0'}"></span><div><strong>${esc(g.name)}</strong><small>${esc(g.result)} · ${timeAgo(g.ts)}</small></div></div>`).join('') : '<p style="font-size:12px;color:var(--muted)">아직 기록이 없어요.</p>';
  }
}
// 지도 카드에 설정 진입 버튼을 덧붙임(기존 렌더 로직은 그대로 두고 뒤에 이어붙이는 방식)
const _origRenderLocationCard=renderLocationCard;
renderLocationCard=function(){
  _origRenderLocationCard();
  const box=$('#locationCard'); if(!box)return;
  const link=document.createElement('button');
  link.className='ghost-btn'; link.style.cssText='margin-top:8px;width:100%';
  link.textContent='⚙️ 위치 알림 설정(지오펜스)';
  link.onclick=openGeoSettings;
  box.appendChild(link);
};

// ---------- report ----------
function renderReport(){
  const logoImg=$('#wrapHeroLogo'); if(logoImg) logoImg.src=LOGO_DATA;
  const total=library.length+events.length;
  $('#wrapTotal').textContent=total;

  const counts={}; library.forEach(l=>{ (counts[l.category]=counts[l.category]||[]).push(l.title) });
  const top4=Object.entries(counts).sort((a,b)=>b[1].length-a[1].length).slice(0,4);
  const grid=$('#interestGrid');
  grid.innerHTML = top4.length? top4.map(([cat,titles])=>{
    const bg=CAT_TINT[cat]||'#EFEAE0';
    const sub=titles.slice(0,3).map(t=>t.length>7?t.slice(0,7)+'…':t).join(' · ');
    return `<div class="icard" style="background:${bg}"><div class="ilabel">${CAT_EMOJI[cat]||'📁'} ${esc(cat)}</div><div class="inum">${titles.length}</div><div class="isub">${esc(sub)}</div></div>`;
  }).join('') : '<p style="font-size:12px;color:var(--muted);grid-column:1/-1">아직 데이터가 부족해요.</p>';

  const aiEvents=events.filter(e=>e.source&&e.source.includes('AI'));
  const kwBank=['마감','예약','세미나','발표','시험','생일','약속','신청'];
  const kws=[]; aiEvents.forEach(e=>kwBank.forEach(k=>{ if(e.title.includes(k)&&!kws.includes(k)) kws.push(k) }));
  const notifyCount=(geoLog?geoLog.filter(g=>g.result==='알림').length:0)+recent.filter(r=>r.label&&r.label.startsWith('위치 알림')).length;
  const placeCounts={}; library.forEach(l=>{ if(l.place) placeCounts[l.place]=(placeCounts[l.place]||0)+1 });
  const topPlaces=Object.entries(placeCounts).sort((a,b)=>b[1]-a[1]).map(([p])=>p);

  const moments=[
    {icon:'📌',title:`일정 ${aiEvents.length}건을 놓치지 않게 했어요`,sub:kws.slice(0,4).join(' · ')||'캘린더 자동 등록'},
    {icon:'🔔',title:`필요한 순간 ${notifyCount}번 다시 알려드렸어요`,sub:'쿠폰 · 저장한 맛집 · 여행지'},
  ];
  if(topPlaces.length) moments.push({icon:'📍',title:`가장 많이 저장한 지역은 ${topPlaces[0]}예요`,sub:topPlaces.slice(0,3).join(' → ')});
  $('#momentsCard').innerHTML=moments.map(m=>`<div class="moment-row"><div class="micon">${m.icon}</div><div><strong>${esc(m.title)}</strong><small>${esc(m.sub)}</small></div></div>`).join('');
}
const genBtn=$('#genWrapped');
if(genBtn) genBtn.onclick=async()=>{
  genBtn.disabled=true; genBtn.textContent='생성 중...';
  const out=$('#wrappedText'); out.textContent='생각하는 중...';
  try{
    const sample=await claude.use('sample');
    if(!sample){out.textContent='AI 요약을 쓰려면 이 화면에서 Claude 사용을 허용해주세요.';genBtn.disabled=false;genBtn.textContent='다시 시도';return}
    const libText=library.map(l=>`- [${l.category}] ${l.title}${l.place?' ('+l.place+')':''}${l.note?' · '+l.note:''}`).join('\n')||'(없음)';
    const evText=events.map(e=>`- ${e.date} ${e.title}`).join('\n')||'(없음)';
    const prompt=`아래는 한 사용자가 Snaptok에 저장해 둔 정보입니다.\n\n[보관함]\n${libText}\n\n[일정]\n${evText}\n\n이 사람의 관심사와 생활 패턴을 정중한 존댓말로 3문장으로 요약하고, 놓치기 쉬워 보이는 부분을 마지막 한 문장으로 짚어주세요. 총 4문장 이내, 다른 설명이나 목록 없이 문단으로만 답하세요.`;
    const {text}=await sample(prompt,{modelTier:'default',onText:({text})=>{out.textContent=text}});
    out.textContent=text; genBtn.textContent='다시 생성';
  }catch(e){
    out.textContent='요약을 만들지 못했어요 ('+(e&&e.code||'오류')+'). 다시 시도해주세요.';
    genBtn.textContent='다시 시도';
  }
  genBtn.disabled=false;
};

// ---------- AI: image analysis ----------
function fileToCompressed(file,max=800,quality=.7){
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onerror=reject;
    reader.onload=()=>{
      const img=new Image();
      img.onerror=reject;
      img.onload=()=>{
        let {width,height}=img; const scale=Math.min(1,max/Math.max(width,height));
        width=Math.round(width*scale); height=Math.round(height*scale);
        const canvas=document.createElement('canvas'); canvas.width=width; canvas.height=height;
        canvas.getContext('2d').drawImage(img,0,0,width,height);
        const dataUrl=canvas.toDataURL('image/jpeg',quality);
        canvas.toBlob(blob=>resolve({blob,dataUrl}),'image/jpeg',quality);
      };
      img.src=reader.result;
    };
    reader.readAsDataURL(file);
  });
}
function keywordFallback(filename){
  const map=[['맛집',['food','cafe','restaurant','맛집','카페']],['쿠폰',['coupon','gifticon','쿠폰','기프티콘']],
  ['여행지',['trip','travel','여행']],['패션',['fashion','clothes','옷','shoes']],['공모전',['contest','공모전','대외활동']],
  ['전시회',['expo','exhibition','전시']],['영화',['movie','영화']],['콘서트',['concert','콘서트']]];
  const name=filename.toLowerCase();
  for(const [cat,words] of map) if(words.some(w=>name.includes(w))) return cat;
  return '기타';
}
// 서버 /api/analyze 호출. 서버가 분석·저장하고 결과를 돌려준다.
// 웹은 결과의 saved 항목을 기존 localStorage(addEventAuto/addLibraryAuto)에 반영한다.
async function analyzeOne(file){
  // 분석용: 긴 변 1600px, 품질 0.85 (텍스트 판독력 확보)
  const analysisImg=await fileToCompressed(file,1600,0.85);
  // 화면·저장용 썸네일: 800px, 0.7 (localStorage 절약)
  const thumb=await fileToCompressed(file,800,0.7);
  const base={filename:file.name,dataUrl:thumb.dataUrl};
  const fd=new FormData();
  fd.append('image',analysisImg.blob,file.name);
  fd.append('request_id','web-'+Date.now()+'-'+Math.random().toString(16).slice(2));
  try{
    const resp=await fetch('/api/analyze',{method:'POST',body:fd});
    if(!resp.ok) throw new Error('http '+resp.status);
    const data=await resp.json();
    return {...base,server:data,decision:data.decision,summary:data.summary};
  }catch(e){
    console.warn('analyze failed',e);
    return {...base,server:null,decision:'review',error:String(e&&e.message||e)};
  }
}

// ---------- add menu / batch flow ----------
function openAddMenu(){
  setSheet(grab+`<span class="chip">새 정보 추가</span><h2>Snaptok에<br>무엇을 맡길까요?</h2>
  <p class="copy" id="aiCapNote">AI 연결 상태 확인 중...</p>
  <button class="choice" id="pickFiles"><i>▧</i><span><strong>스크린샷 · 사진 선택</strong><small>여러 장을 AI가 각각 분석</small></span></button>
  <button class="choice" id="pickCamera"><i>⌾</i><span><strong>카메라로 촬영</strong><small>포스터·메뉴 등을 직접 촬영</small></span></button>
  <button class="secondary" id="closeAdd">닫기</button>`);
  $('#closeAdd').onclick=closeSheet;
  $('#pickFiles').onclick=()=>pick(false);
  $('#pickCamera').onclick=()=>pick(true);
  checkAiCapability();
}
async function checkAiCapability(){
  const note=$('#aiCapNote'); if(!note)return;
  try{
    const r=await fetch('/api/health'); const h=await r.json();
    note.textContent=`✅ 서버 분석 연결됨 · ${h.llm_mode==='live'?'AI 실사용':'mock 모드'}`;
  }catch(e){ note.textContent='⚠️ 서버에 연결할 수 없어요. /app 이 아닌 file:// 로 열면 분석이 안 돼요.'; }
}
function pick(camera){
  const input=document.createElement('input'); input.type='file'; input.accept='image/jpeg,image/png,image/webp';
  if(!camera)input.multiple=true; else input.setAttribute('capture','environment');
  input.onchange=async()=>{
    let files=[...input.files]; if(!files.length)return;
    if(files.length>8){files=files.slice(0,8);toast('한 번에 최대 8장까지 분석해요','앞의 8장만 선택했습니다.')}
    const bad=files.find(f=>f.size>8*1024*1024);
    if(bad){toast('8MB 이하 이미지를 선택해주세요',bad.name);return}
    await runAnalysis(files);
  };
  input.click();
}
function renderBatchList(display){
  const list=$('#bList'); if(!list)return;
  list.innerHTML=display.map(r=>r.pending?`<div class="batch-row"><div class="thumb">⏳</div><div><strong>${esc(r.filename)}</strong><small>분석 중...</small></div><div></div></div>`:rowMini(r)).join('');
}
// 서버 분석 결과(results 배열)를 localStorage 에 반영. 분석 즉시 저장(사용자 확인 불필요).
// 반환: {addedEvents, addedLib, dupSkipped, queued, geoNames[]}
function applyServerResults(meta){
  const stat={addedEvents:0,addedLib:0,dupSkipped:0,queued:0,geoNames:[]};
  const data=meta.server;
  if(!data || meta.decision==='review' && (!data || !data.results || !data.results.length)){
    // 서버 오류 또는 확인 필요 -> 확인 필요 큐로
    pendingReview=[{id:'pend-'+Date.now()+Math.random().toString(16).slice(2),title:meta.filename.replace(/\.[^.]+$/,'')||'확인 필요',category:'기타',place:'',note:meta.error?('분석 실패 · '+meta.error):'확인이 필요해요',date:null,time:null,confidence:.3,dataUrl:meta.dataUrl},...pendingReview];
    stat.queued++;
    return stat;
  }
  stat.missedMsgs=[];
  (data.results||[]).forEach(r=>{
    if(r.status==='dup'){stat.dupSkipped++; return;}
    if(r.kind==='review'){stat.queued++;
      pendingReview=[{id:'pend-'+Date.now()+Math.random().toString(16).slice(2),title:r.title||'확인 필요',category:'기타',place:'',note:'확인이 필요해요',date:null,time:null,confidence:.4,dataUrl:meta.dataUrl},...pendingReview];
      return;}
    const it=r.item||{};
    if(r.kind==='event'){
      // 서버가 준 날짜 필드(date/time, 폴백 due/start/end)를 그대로 읽는다. TODAY 로 채우지 않는다.
      const evDate=it.date||it.due||it.start||it.end||null;
      if(!evDate){
        // 날짜 없는 행동 항목은 일정으로 저장하지 않고 확인 필요로
        stat.queued++;
        pendingReview=[{id:'pend-'+Date.now()+Math.random().toString(16).slice(2),title:it.title||r.title||'확인 필요',category:it.category||'기타',place:it.location||'',note:'날짜를 확인하지 못했어요',date:null,time:null,confidence:.4,dataUrl:meta.dataUrl},...pendingReview];
        return;
      }
      const res=addEventAuto({date:evDate,time:it.time||'시간 미정',title:it.title,location:it.location||'',image:meta.dataUrl,date_role:it.date_role},it.source||'Snaptok AI');
      if(res.status==='added')stat.addedEvents++; else stat.dupSkipped++;
    } else if(r.kind==='library'){
      const res=addLibraryAuto({title:it.title,category:it.category||'기타',place:it.place||'',note:it.note||'',confidence:.9,image:meta.dataUrl,
        geoType:it.geoType,lat:it.lat,lng:it.lng,radius:it.radius,area:it.area,brand:it.brand,branches:it.branches,expiry:it.expiry,used:it.used,
        missed:it.missed,missed_date:it.missed_date,date_role:it.date_role},it.source||'Snaptok AI');
      if(res.status==='added'){
        stat.addedLib++;
        if(it.geo_enabled)stat.geoNames.push(it.title);
        // 지난 마감 -> 배너 메시지(연도 포함)
        if(it.missed && it.missed_date){ stat.missedMsgs.push(`이미 지난 마감이에요 (${fmtDateY(it.missed_date)})`); }
      } else stat.dupSkipped++;
    }
  });
  return stat;
}
// 날짜를 연도 포함해 보여준다(올해가 아니면 반드시 연도 표시). YYYY-MM-DD -> "2025.8.31"
function fmtDateY(d){
  if(!d) return '';
  const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(d);
  if(!m) return d;
  return `${m[1]}.${Number(m[2])}.${Number(m[3])}`;
}
// 화면 표시용: 올해면 M.D, 다른 해면 YYYY.M.D
function fmtDateShort(d){
  if(!d) return '';
  const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(d);
  if(!m) return d;
  const curY=String(new Date().getFullYear());
  return m[1]===curY ? `${Number(m[2])}.${Number(m[3])}` : `${m[1]}.${Number(m[2])}.${Number(m[3])}`;
}

async function runAnalysis(files){
  setSheet(grab+`<span class="chip navy" id="aiStatusChip">서버 분석 중</span><h2><span id="bNow">0</span> / ${files.length}장 읽는 중</h2><p class="copy">이미지를 서버로 보내 행동·기억·불확실로 나눕니다. 분석 즉시 자동 저장돼요.</p><div class="progress"><span id="bBar"></span></div><div id="bList"></div>`);
  const display=files.map(f=>({pending:true,filename:f.name}));
  renderBatchList(display);
  const results=[];
  const total={addedEvents:0,addedLib:0,dupSkipped:0,queued:0,geoNames:[],missedMsgs:[]};
  for(let i=0;i<files.length;i++){
    const meta=await analyzeOne(files[i]);
    // 분석 즉시 저장
    const stat=applyServerResults(meta);
    total.addedEvents+=stat.addedEvents; total.addedLib+=stat.addedLib;
    total.dupSkipped+=stat.dupSkipped; total.queued+=stat.queued;
    stat.geoNames.forEach(n=>total.geoNames.push(n));
    (stat.missedMsgs||[]).forEach(m=>total.missedMsgs.push(m));
    meta.stat=stat;
    results[i]=meta; display[i]={...meta,pending:false,
      title:(meta.server&&meta.server.results&&meta.server.results[0]&&meta.server.results[0].title)||meta.filename,
      badge:(meta.decision||'').toUpperCase()};
    const now=$('#bNow'),bar=$('#bBar'); if(now)now.textContent=String(i+1); if(bar)bar.style.width=((i+1)/files.length*100)+'%';
    renderBatchList(display);
  }
  showResult(results,total);
}

// 결과 시트: 확인 버튼 하나. 저장은 이미 끝났다.
function showResult(results,total){
  const rows=results.map(r=>rowMini(r)).join('');
  setSheet(grab+`<span class="chip navy">처리 완료</span>
  <h2>${results.length}장을 처리했어요</h2>
  <p class="copy">확실한 건 자동으로 저장했어요. 확인 필요 항목은 오늘 화면의 '확인 필요'에서 골라주세요.</p>
  <div id="bList">${rows}</div>
  <div class="decision"><button class="a" id="revOk">확인</button></div>`);
  $('#revOk').onclick=closeSheet;
  // 저장 완료 배너
  const parts=[];
  if(total.addedEvents)parts.push(`캘린더 ${total.addedEvents}건`);
  if(total.addedLib)parts.push(`보관함 ${total.addedLib}건`);
  if(total.queued)parts.push(`확인 필요 ${total.queued}건`);
  if(total.dupSkipped)parts.push(`중복 ${total.dupSkipped}건`);
  let sub='';
  if(total.missedMsgs&&total.missedMsgs.length) sub=total.missedMsgs[0];
  else if(total.geoNames.length) sub=`${total.geoNames[0]} · 근처에 가면 알려드릴게요`;
  push(parts.join(' · ')||'변경사항이 없어요', sub);
  renderToday(); renderCalendar(); renderLibrary(); renderActivity();
}
function rowMini(r){
  const badges=(r.server&&r.server.results?r.server.results:[]).map(x=>`<span class="badge ${x.status==='dup'?'rev':(x.kind==='event'?'act':(x.kind==='review'?'rev':'mem'))}">${esc(x.badge||'')}</span>`).join(' ')||'<span class="badge rev">확인 필요</span>';
  return `<div class="batch-row"><div class="thumb"><img src="${r.dataUrl}"></div><div><strong>${esc(r.title||r.filename)}</strong><small>${esc(r.summary||'')}</small>${badges}</div><div></div></div>`;
}

// ---------- init ----------
if(triggers.some(t=>t.active) && permState==='granted') ensureWatcher();
renderToday(); renderCalendar(); renderLibrary(); renderActivity(); renderReport();
})();
