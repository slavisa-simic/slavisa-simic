const cfg = await (await fetch('../config/network.json')).json();
const mobile = innerWidth <= 600;
const variant = mobile ? 'mobile' : 'desktop';
const core = cfg.core[variant];
const layout = cfg.exports[variant];
const esc = value => String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const text = (x,y,value,size,fill,extra='') => `<text x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(value)}</text>`;
const route = points => points.map((p,i) => `${i?'L':'M'}${p[0]} ${p[1]}`).join('');
function projectMarkup(project) {
  const box = project[variant].box;
  const [x,y,w,h] = box;
  const left = x + (mobile ? 12 : 22);
  const color = cfg.theme[project.color];
  const end = project[variant].input;
  const lines = project[variant].route;
  const border = project.color === 'blue' ? '#343d48' : '#43383d';
  let markup = `<path d="${route(lines)}" fill="none" stroke="url(#${project.id}-wire)" stroke-width="1.3"/>`;
  if (project[variant].secondary_route) markup += `<path d="${route(project[variant].secondary_route)}" fill="none" stroke="#393e47" stroke-width=".7"/>`;
  markup += `<rect x="${end[0]-2.5}" y="${end[1]-3.5}" width="5" height="7" fill="#111315" stroke="${color}" stroke-width=".8"/>`;
  markup += `<a href="${esc(project.repository)}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="3" fill="${cfg.theme.surface}" stroke="${border}" stroke-width="1"/><path d="M${x} ${y}h${mobile?22:50}" stroke="${color}" stroke-width="2"/>`;
  if (mobile) {
    markup += text(left,y+16,`${project.sequence} / ${project.id==='vigil'?'APP':'AI'}`,7,color,'class="m" letter-spacing=".6"');
    markup += text(left,y+35,project.name,16,cfg.theme.text,'font-weight="550" letter-spacing="-.5"');
    project.mobile.summary.forEach((s,i)=>markup += text(left,y+57+i*13,s,8,'#b8c1ce'));
    markup += `<path d="M${left} ${y+83}H${x+w-12}" stroke="#2c3037" stroke-width=".8"/>`;
    project.mobile.technology.forEach((s,i)=>markup+=text(left,y+103+i*16,s,project.id==='vigil'?7.5:7,'#c3cbd7',i===0?'class="m"':''));
  } else {
    markup += text(left,y+28,`${project.sequence} / ${project.category}`,9,color,'class="m" letter-spacing="1.2"');
    markup += text(left,y+65,project.name,26,cfg.theme.text,'font-weight="550" letter-spacing="-.7"');
    markup += text(left,y+90,project.subtitle,13,'#b8c1ce');
    project.summary.forEach((s,i)=>markup += text(left,y+121+i*19,s,12,'#a7aeb9'));
    markup += `<path d="M${left} ${y+159}H${x+w-22}" stroke="#2c3037" stroke-width=".8"/>`;
    markup += text(left,y+181,'PROJECT TECHNOLOGIES',8,'#919aa8','class="m" letter-spacing="1.1"');
    project.technology.forEach((s,i)=>markup += text(left,y+203+i*19,s,11,'#c3cbd7'));
    if(project.note) markup += text(left,y+222,project.note,10,'#929aa6');
    markup += text(left,y+251,project.repository_label,10,color,'class="m"');
    markup += text(x+w-23,y+251,'↗',14,color,'text-anchor="end"');
  }
  return markup + '</a>';
}
function coreMarkup() {
  const [x,y,w,h] = core.box;
  const [lx,ly,lw,lh] = core.logo;
  const cx = x+w/2;
  return text(cx,mobile?70:108,'SYSTEM CORE',mobile?7.5:10,'#dce0e7','class="m" text-anchor="middle" letter-spacing="1.3"') +
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="3" fill="#141619" stroke="#5b626e" stroke-width=".9"/><path d="M${x} ${y+14}v-14h14M${x+w-14} ${y}h14v14M${x+w} ${y+h-14}v14h-14M${x+14} ${y+h}h-14v-14" fill="none" stroke="#b8bfc9" stroke-width="1"/><image class="logo-layer" href="../assets/blueprint/source/logo.png" x="${lx}" y="${ly}" width="${lw}" height="${lh}" preserveAspectRatio="xMidYMid meet"/>` +
    text(cx,mobile?184:299,cfg.identity.name,mobile?8:12,'#b8bfc9','text-anchor="middle"') +
    text(cx,mobile?201:320,mobile?'DEVELOPER':'ENGINEERING IDENTITY',mobile?6:9,'#929aa6','class="m" text-anchor="middle" letter-spacing="1"');
}
const title = mobile ? 'Selected work, connected.' : 'Selected work, connected.';
let drawing = `<svg viewBox="0 0 ${layout.diagram_width} ${layout.diagram_height}" xmlns="http://www.w3.org/2000/svg"><defs>`;
for (const p of cfg.projects) drawing += `<linearGradient id="${p.id}-wire" x1="${p[variant].route[0][0]}" y1="0" x2="${p[variant].input[0]}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="#b9bfc8"/><stop offset="1" stop-color="${cfg.theme[p.color]}"/></linearGradient>`;
drawing += '</defs>';
if (!mobile) {
  drawing += '<path d="M16 28h12M22 22v12M996 28h12M1002 22v12M16 402h12M22 396v12M996 402h12M1002 396v12" stroke="#555b65" stroke-width=".8"/>';
  drawing += text(40,34,'PROJECTS / SOURCE REPOSITORIES',10,'#858e9a','class="m" letter-spacing="1.1"') + text(984,34,'slavisa-simic',10,'#858e9a','class="m" text-anchor="end"');
}
cfg.projects.forEach(p=>drawing+=projectMarkup(p));
drawing += coreMarkup();
if(!mobile) drawing += text(40,400,'DEVELOPER → PROJECTS → TECHNOLOGIES',9,'#858e9a','class="m"')+text(984,400,'PUBLIC SOURCE ON GITHUB',9,'#858e9a','class="m" text-anchor="end"');
drawing += '</svg>';
document.querySelector('#hero').style.width=`${layout.width}px`;
document.querySelector('#hero').style.setProperty('--pad',`${layout.padding}px`);
document.querySelector('#hero').innerHTML = `
<header class="row masthead" data-row="masthead"><a class="brand" href="${cfg.identity.github}"><img src="../assets/blueprint/source/logo.png" alt="Original S logo"><span>SLAVIŠA SIMIĆ</span></a><a class="nav-cell" href="${cfg.identity.github}">GitHub <span class="arrow">↗</span></a><a class="nav-cell" href="${cfg.identity.linkedin}">LinkedIn <span class="arrow">↗</span></a></header>
<section class="row identity" data-row="identity"><h1>${esc(cfg.identity.name)}</h1><p class="role">${esc(cfg.identity.role)}</p><p class="intro">${cfg.identity.intro.map(esc).join('<br>')}</p><div class="network-heading"><h2>${title}</h2><span class="eyebrow">Portfolio architecture / 01</span></div></section>
<section class="row network-row" data-row="network"><div class="network">${drawing}</div></section>
<section class="row legend-row" data-row="legend"><div class="legend"><span class="legend-item"><i class="key"></i>Identity</span><span class="legend-item"><i class="key blue"></i>Application</span><span class="legend-item"><i class="key red"></i>AI case study</span><span class="reference">PORTFOLIO / SYSTEM VIEW</span></div></section>
<section class="row practice-row" data-row="practice"><div class="practice"><div><h3 class="skill-title">PERSONAL SKILLS / BACKEND ENGINEERING</h3><p class="skills">${cfg.identity.personal_skills.map(esc).join('<br>')}</p></div><div><h3 class="skill-title">AI DEVELOPMENT TOOLS</h3><p class="codex">${esc(cfg.identity.ai_tool)}</p><p class="tool-note">${esc(cfg.identity.ai_note)}</p></div></div></section>
<footer class="row footer-row" data-row="footer"><div class="footer"><a href="${cfg.identity.github}?tab=repositories">Explore the repositories <span class="arrow">↗</span></a><span>github.com/slavisa-simic</span></div></footer>`;
if (new URLSearchParams(location.search).has('base')) document.body.classList.add('base');
window.blueprintReady = true;
