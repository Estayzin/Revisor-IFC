# patch2_explorer.py — fixes pendientes
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = r'C:\Users\Usuario\Documents\GitHub\Revisor-IFC\explorer.html'

with open(SRC, encoding='utf-8') as f:
    s = f.read()

# FIX A: verificarNiveles — el texto exacto puede variar, buscar por partes
old_push = "res.push({id:'#'+id,nombre:nombre,largo:nombre.length,ok:nombre.length===5});"
new_push = """var coords=getCoordenadas(instancias[id],instancias,texto);
      var elev=coords?coords.z:null;
      if((elev===null||elev===0)&&attrs[9]){var ea=parseFloat(attrs[9]);if(!isNaN(ea))elev=ea;}
      res.push({id:'#'+id,nombre:nombre,largo:nombre.length,ok:nombre.length===5,elev:elev||0});"""

if old_push in s:
    s = s.replace(old_push, new_push, 1)
    print('OK: verificarNiveles push')
else:
    print('SKIP: verificarNiveles push ya aplicado o no encontrado')

# Agregar sort antes del return de verificarNiveles
old_ret = "  return res;\n}\n\nfunction extraerRaw"
new_ret = "  res.sort(function(a,b){return a.elev-b.elev;});\n  return res;\n}\n\nfunction extraerRaw"
if old_ret in s:
    s = s.replace(old_ret, new_ret, 1)
    print('OK: verificarNiveles sort')
elif 'res.sort(function(a,b){return a.elev' in s:
    print('SKIP: sort ya aplicado')
else:
    print('ERROR: no encontrado return verificarNiveles')

# FIX B: renderReporte completo
REPORTE_NEW = '''/* ═══ RENDER REPORTE ═══ */
function rpSec(title,badge,bc,bodyHtml,openDefault){
  var uid='rps'+Math.random().toString(36).substr(2,5);
  var arr=openDefault?'&#9662;':'&#9658;';
  var bodyStyle=openDefault?'':'display:none';
  return '<div class="rp-sec">'+
    '<div class="rp-sec-hdr" onclick="rpToggle(\''+uid+'\')">'+
    '<span class="rp-sec-title">'+title+'</span>'+
    '<span class="rp-badge '+bc+'">'+badge+'</span>'+
    '&nbsp;<span class="rp-arr" id="arr_'+uid+'">'+arr+'</span>'+
    '</div>'+
    '<div class="rp-content" id="'+uid+'" style="'+bodyStyle+'">'+bodyHtml+'</div>'+
    '</div>';
}
function rpToggle(uid){
  var el=document.getElementById(uid),arr=document.getElementById('arr_'+uid);
  var open=el.style.display==='none';
  el.style.display=open?'':'none';
  arr.innerHTML=open?'&#9662;':'&#9658;';
}
function tipoGrupoToggle(uid){
  var el=document.getElementById(uid),arr=document.getElementById('arr_'+uid);
  var open=el.style.display==='none'||el.style.display==='';
  document.querySelectorAll('.rp-tipo-items').forEach(function(x){x.style.display='none';});
  document.querySelectorAll('.rp-tipo-grupo-arr').forEach(function(x){x.classList.remove('open');});
  if(open&&el.style.display!=='block'){el.style.display='block';arr.classList.add('open');}
}
function renderTiposElemento(tiposXClase){
  if(!tiposXClase||!Object.keys(tiposXClase).length)
    return '<div class="rp-msg">No se detectaron tipos.</div>';
  var html='<div class="rp-hl-hint">&#9658; Clic en tipo para resaltar en 3D</div>';
  Object.keys(tiposXClase).sort().forEach(function(cls,ci){
    var tipos=tiposXClase[cls];
    var tiposOrd=Object.keys(tipos).sort(function(a,b){return tipos[b]-tipos[a];});
    var totalCls=tiposOrd.reduce(function(s,t){return s+tipos[t];},0);
    var uid='te'+ci+'_'+Math.random().toString(36).substr(2,4);
    var nomCls=ESP_ENTS.reduce(function(a,e){return e[0]===cls?e[1]:a;},'')
               ||cls.charAt(0)+cls.slice(1).toLowerCase();
    var col=CAT_COLORS[cls]||CAT_COLORS.DEFAULT;
    var dot='rgb('+(col.map(function(v){return Math.round(v*255);})).join(',')+')';
    var itemsHtml=tiposOrd.map(function(tipo){
      var qty=tipos[tipo];
      var tipoEsc=tipo.replace(/\'/g,"\\\'").replace(/"/g,'&quot;');
      var hasMesh=meshes.some(function(m){return m.userData.cls===cls&&m.userData.tipo===tipo;});
      var attrs=hasMesh?' data-cls="'+cls+'" data-tipo="'+tipoEsc+'" onclick="hlSelectTipoElem(event,\''+cls+'\',\''+tipoEsc+'\')"':'';
      return '<div class="rp-tipo-item'+(hasMesh?' has-mesh':'')+'"'+attrs+'>'+
        '<div class="rp-tipo-item-dot" style="background:'+dot+'"></div>'+
        '<div class="rp-tipo-item-name">'+esc(tipo)+'</div>'+
        '<div class="rp-tipo-item-qty">'+qty+'</div></div>';
    }).join('');
    html+='<div class="rp-tipo-grupo">'+
      '<div class="rp-tipo-grupo-hdr" onclick="tipoGrupoToggle(\''+uid+'\')">'+
        '<div style="width:8px;height:8px;border-radius:50%;background:'+dot+';flex-shrink:0"></div>'+
        '<span class="rp-tipo-grupo-name">'+nomCls+'</span>'+
        '<span class="rp-tipo-grupo-count">'+totalCls+'</span>'+
        '<span class="rp-tipo-grupo-arr" id="arr_'+uid+'">&#9658;</span>'+
      '</div>'+
      '<div class="rp-tipo-items" id="'+uid+'">'+itemsHtml+'</div></div>';
  });
  return html;
}
function renderReporte(est){
  var html='',conteo=est.conteo;

  /* 1 - Origen */
  var orig=verificarOrigen(est);
  if(orig.length){
    var origOk=orig.every(function(r){return r.ok;});
    var origFilas=orig.map(function(r){
      var coords=r.x!==null?'('+[r.x,r.y,r.z].map(function(v){return(+v).toFixed(3);}).join(', ')+')':'N/A';
      return '<tr><td class="td-name">'+r.tipo.charAt(0)+r.tipo.slice(1).toLowerCase()+'<div class="td-cls">'+esc(r.nombre)+'</div></td>'+
        '<td style="font:400 9px var(--mono);color:var(--muted)">'+coords+'</td>'+
        '<td class="td-ok">'+(r.ok?'<span class="ic-ok">&#10003;</span>':'<span class="ic-err">&#10007;</span>')+'</td></tr>';
    }).join('');
    html+=rpSec('Origen (0,0,0)',origOk?'OK':'Error',origOk?'rp-ok':'rp-err','<table class="rp-table">'+origFilas+'</table>',!origOk);
  }

  /* 2 - Nombres */
  var noms=verificarNombres(est);
  if(noms.length){
    var nomsOk=noms.every(function(r){return r.ok;});
    var nomsFilas=noms.map(function(r){
      return '<tr><td class="td-name">'+r.tipo.charAt(0)+r.tipo.slice(1).toLowerCase()+'</td>'+
        '<td>"'+esc(r.nombre)+'" ('+r.largo+' car.)</td>'+
        '<td class="td-ok">'+(r.ok?'<span class="ic-ok">&#10003;</span>':'<span class="ic-err">&#10007;</span>')+'</td></tr>';
    }).join('');
    html+=rpSec('Nombres Sitio/Edificio',nomsOk?'OK':'Error',nomsOk?'rp-ok':'rp-err',
      '<div class="rp-msg">Sitio: 3 car. &middot; Edificio: 2 car.</div>'+
      '<table class="rp-table">'+nomsFilas+'</table>',!nomsOk);
  }

  /* 3 - Niveles clickeables */
  var nivs=verificarNiveles(est);
  if(nivs.length){
    var nivsOk=nivs.every(function(r){return r.ok;});
    var nOk=nivs.filter(function(r){return r.ok;}).length;
    var nivsHtml=nivs.map(function(r,idx){
      var elev=typeof r.elev==='number'?r.elev.toFixed(2)+'m':'?';
      var badge=r.ok?'<span class="rp-nivel-item-badge badge-ok">5 car.</span>':'<span class="rp-nivel-item-badge badge-warn">'+r.largo+' car.</span>';
      return '<div class="rp-nivel-item" data-idx="'+idx+'" onclick="hlSelectNivel('+idx+','+JSON.stringify(nivs)+')">'+
        '<div style="flex:1;min-width:0">'+
          '<div class="rp-nivel-item-name">'+esc(r.nombre||'(sin nombre)')+'</div>'+
          '<div class="rp-nivel-item-sub">z = '+elev+'</div>'+
        '</div>'+badge+'</div>';
    }).join('');
    html+=rpSec('Niveles (5 car.)',nOk+'/'+nivs.length+' OK',nivsOk?'rp-ok':nOk>0?'rp-warn':'rp-err',nivsHtml,true);
  }

  /* 4 - Entidades */
  var filas='',presentes=0;
  ESP_ENTS.forEach(function(e){
    var cls=e[0],nom=e[1],qty=conteo[cls]||0;
    if(qty>0)presentes++;
    var hasMesh=meshes.some(function(m){return m.userData.cls===cls;});
    var trCls=hasMesh?' class="has-mesh" onclick="hlSelect(\''+cls+'\')"':'';
    filas+='<tr'+trCls+'><td class="td-name">'+nom+'<div class="td-cls">'+cls.charAt(0)+cls.slice(1).toLowerCase()+'</div></td>'+
      '<td class="td-qty'+(qty===0?' zero':'')+'">'+qty+'</td>'+
      '<td class="td-ok">'+(qty>0?'<span class="ic-ok">&#10003;</span>':'<span class="ic-err">&#10007;</span>')+'</td></tr>';
  });
  var pct=ESP_ENTS.length?Math.round(presentes/ESP_ENTS.length*100):0;
  html+=rpSec('Entidades IFC',presentes+'/'+ESP_ENTS.length,pct===100?'rp-ok':pct>50?'rp-warn':'rp-err',
    '<div class="rp-hl-hint">&#9658; Clic en fila para resaltar en 3D</div><table class="rp-table">'+filas+'</table>',false);

  /* 5 - Tipos */
  if(est.tiposXClase&&Object.keys(est.tiposXClase).length)
    html+=rpSec('Tipos de Elementos','familias','rp-info',renderTiposElemento(est.tiposXClase),false);

  document.getElementById('rpBody').innerHTML=html;
}'''

# Buscar y reemplazar el bloque completo
idx = s.find('/* ═══ RENDER REPORTE ═══ */')
if idx == -1:
    print('ERROR: no encontrado RENDER REPORTE')
else:
    end = s.find('\n/* ═══ CARGA IFC ═══ */', idx)
    if end == -1:
        print('ERROR: no encontrado fin de RENDER REPORTE')
    elif 'renderTiposElemento' in s[idx:end]:
        print('SKIP: renderReporte ya completo')
    else:
        s = s[:idx] + REPORTE_NEW + '\n' + s[end:]
        print('OK: renderReporte reemplazado (5 secciones + tipos)')

# hlSelect — necesaria para el click en tabla entidades
HL_SELECT = '''
function hlSelect(cls){
  if(hlActiveCls===cls){hlClear();return;}
  hlActiveCls=cls;hlActiveTipo=null;hlActiveNivel=null;
  meshes.forEach(function(m){
    if(m.userData.cls===cls){m.material.color.set(0x00d4ff);m.material.transparent=false;m.material.opacity=1;}
    else{m.material.color.set(0x1a2a40);m.material.transparent=true;m.material.opacity=0.18;}
  });
  var target=meshes.find(function(m){return m.userData.cls===cls;});
  if(target){
    var bbox=new THREE.Box3().setFromObject(target),center=bbox.getCenter(new THREE.Vector3()),size=bbox.getSize(new THREE.Vector3()).length();
    controls.target.copy(center);camera.position.set(center.x+size*.7,center.y+size*.5,center.z+size*.7);controls.update();
  }
}'''

if 'function hlSelect(' not in s:
    s = s.replace('function hlSelectTipoElem(', HL_SELECT + '\nfunction hlSelectTipoElem(', 1)
    print('OK: hlSelect insertada')
else:
    print('SKIP: hlSelect ya existe')

# Verificacion final
checks = {
    'FORMA': 'var FORMA=' in s,
    'tiposXClaseXStorey': 'tiposXClaseXStorey' in s,
    'globos3d': 'globos3d' in s,
    'tooltip3d': 'id="tooltip3d"' in s,
    'hlSelectNivel': 'hlSelectNivel' in s,
    'hlSelect(': 'function hlSelect(' in s,
    'renderTiposElemento': 'renderTiposElemento' in s,
    'elipsoides': 'esGlobo' in s,
    'onCanvasMouseMove': 'onCanvasMouseMove' in s,
    'nivel clickeable': 'rp-nivel-item' in s,
    'UTF8 limpio': chr(0xfffd) not in s,
}
print()
print('=== Verificacion final ===')
ok_count = 0
for k,v in checks.items():
    ok_count += 1 if v else 0
    print(f'  {"OK" if v else "ERROR"}: {k}')

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(s)
print(f'\nGuardado ({s.count(chr(10))} lineas) — {ok_count}/{len(checks)} checks OK')
