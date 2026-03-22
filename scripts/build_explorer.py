# build_explorer.py — Aplica todos los cambios de sesión sobre el archivo base git
# Uso: py build_explorer.py
# Idempotente: detecta si ya fue aplicado y no duplica.

import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = r'C:\Users\Usuario\Documents\GitHub\Revisor-IFC\explorer.html'

with open(SRC, encoding='utf-8') as f:
    s = f.read()

ok = []
err = []

def patch(label, old, new):
    global s
    if new.strip() in s:
        ok.append('SKIP ' + label)
        return
    if old not in s:
        err.append('NOT FOUND: ' + label)
        return
    s = s.replace(old, new, 1)
    ok.append('OK   ' + label)

def patch_fn(label, fn_name, new_body):
    """Reemplaza una función completa buscándola por nombre."""
    global s
    if '%%%DONE:' + label + '%%%' in s:
        ok.append('SKIP ' + label)
        return
    idx = s.find('function ' + fn_name + '(')
    if idx == -1:
        err.append('NOT FOUND fn: ' + label)
        return
    # Buscar el cierre de la función contando llaves
    depth = 0
    start_body = s.index('{', idx)
    i = start_body
    while i < len(s):
        if s[i] == '{': depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    s = s[:idx] + new_body + '\n' + s[end:]
    ok.append('OK   ' + label)

# ═══════════════════════════════════════════════════════════════════
# P1 — Estado global
# ═══════════════════════════════════════════════════════════════════
patch('P1 estado global',
    'var meshes = [], selectedMesh = null;',
    'var meshes = [], selectedMesh = null, globos3d = [];\n'
    'var hlActiveCls = null, hlActiveTipo = null, hlActiveNivel = null;'
)

# ═══════════════════════════════════════════════════════════════════
# P2 — CSS adicional (antes del bloque de panel reporte)
# ═══════════════════════════════════════════════════════════════════
CSS_ADD = '''/* Tooltip 3D */
#tooltip3d{position:fixed;display:none;pointer-events:none;z-index:999;background:rgba(6,13,24,.92);border:1px solid var(--accent);border-radius:5px;padding:7px 10px;min-width:160px;backdrop-filter:blur(4px)}
#tooltip3d .tt-cls{font:700 9px var(--mono);color:var(--accent);text-transform:uppercase;letter-spacing:.1em}
#tooltip3d .tt-nom{font:600 11px var(--sans);color:#e0f0ff;margin-top:2px}
#tooltip3d .tt-sub{font:400 9px var(--mono);color:var(--muted);margin-top:3px;line-height:1.5}
/* Niveles clickeables */
.rp-nivel-item{display:flex;align-items:center;gap:8px;padding:6px 10px;cursor:pointer;transition:background .12s;border-left:2px solid transparent}
.rp-nivel-item:hover{background:rgba(0,212,255,.06)}
.rp-nivel-item.hl-active{background:rgba(0,212,255,.12);border-left-color:var(--accent)}
.rp-nivel-item-name{font:600 10px var(--mono);color:var(--text)}
.rp-nivel-item:hover .rp-nivel-item-name,.rp-nivel-item.hl-active .rp-nivel-item-name{color:var(--accent)}
.rp-nivel-item-sub{font:400 8px var(--mono);color:var(--muted);margin-top:1px}
.rp-nivel-item-badge{font:700 8px var(--mono);padding:2px 5px;border-radius:3px}
.badge-ok{background:rgba(0,200,83,.1);color:#00c853}
.badge-warn{background:rgba(255,107,53,.1);color:var(--warn)}
/* Tipos accordion */
.rp-tipo-grupo{border-bottom:1px solid rgba(26,42,64,.5)}
.rp-tipo-grupo:last-child{border-bottom:none}
.rp-tipo-grupo-hdr{display:flex;align-items:center;gap:6px;padding:5px 10px;cursor:pointer;user-select:none;transition:background .12s}
.rp-tipo-grupo-hdr:hover{background:rgba(0,212,255,.04)}
.rp-tipo-grupo-name{font:700 8px var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.15em;flex:1}
.rp-tipo-grupo-count{font:700 9px var(--mono);color:var(--accent);margin-right:4px}
.rp-tipo-grupo-arr{font-size:9px;color:var(--muted);transition:transform .15s}
.rp-tipo-grupo-arr.open{transform:rotate(90deg)}
.rp-tipo-grupo.no-clasificado .rp-tipo-grupo-name{color:var(--warn)}
.rp-tipo-items{display:none}
.rp-tipo-item{display:flex;align-items:center;gap:6px;padding:5px 10px 5px 26px;cursor:pointer;transition:background .12s;border-left:2px solid transparent}
.rp-tipo-item:hover{background:rgba(0,212,255,.06)}
.rp-tipo-item.hl-active{background:rgba(0,212,255,.12);border-left-color:var(--accent)}
.rp-tipo-item-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.rp-tipo-item-name{font:500 10px var(--mono);color:var(--text);flex:1}
.rp-tipo-item:hover .rp-tipo-item-name,.rp-tipo-item.hl-active .rp-tipo-item-name{color:var(--accent)}
.rp-tipo-item-qty{font:700 9px var(--mono);color:var(--muted)}
.rp-hl-hint{padding:4px 10px 6px;font:400 9px var(--mono);color:var(--muted);opacity:.55}
/* Filas clickeables reporte */
.rp-table tr.has-mesh{cursor:pointer;transition:background .12s}
.rp-table tr.has-mesh:hover{background:rgba(0,212,255,.07)}
.rp-table tr.has-mesh.hl-active{background:rgba(0,212,255,.15)}
.rp-table tr.has-mesh:hover .td-name,.rp-table tr.has-mesh.hl-active .td-name{color:var(--accent)}
/* min-height para scroll correcto */
.view-panel,.panel-3d,.viewer-row,#reportePanel,.rp-body{min-height:0}
'''

patch('P2 CSS adicional',
    '/* ══ PANEL REPORTE LATERAL ══ */',
    CSS_ADD + '/* ══ PANEL REPORTE LATERAL ══ */'
)

# ═══════════════════════════════════════════════════════════════════
# P3 — HTML: tooltip div + ovWelcome mejorado
# ═══════════════════════════════════════════════════════════════════
patch('P3a tooltip div',
    '        </div><!-- /viewer-row -->',
    '''        </div><!-- /viewer-row -->
<div id="tooltip3d">
  <div class="tt-cls" id="ttCls"></div>
  <div class="tt-nom" id="ttNom"></div>
  <div class="tt-sub" id="ttSub"></div>
</div>'''
)

patch('P3b ovWelcome',
    '''            <div class="overlay" id="ovWelcome">
              <div class="ov-icon">&#128230;</div>
              <div class="ov-title">Explorador BIM</div>
              <div class="ov-sub">Sube un archivo .ifc desde el panel izquierdo o arr&aacute;stralo aqu&iacute;.</div>
            </div>''',
    '''            <div class="overlay" id="ovWelcome">
              <div style="text-align:center;max-width:420px;padding:20px">
                <div style="font-size:48px;margin-bottom:16px">&#127959;</div>
                <div style="font:700 18px var(--sans);color:#e0f0ff;margin-bottom:8px">Explorador BIM</div>
                <div style="font:600 11px var(--mono);color:var(--accent);text-transform:uppercase;letter-spacing:.18em;margin-bottom:16px">Revisor IFC &middot; Carlos Estay Ruggieri</div>
                <div style="font:400 12px var(--sans);color:var(--muted);line-height:1.8;margin-bottom:28px">
                  Herramienta de revisi&oacute;n y verificaci&oacute;n de modelos IFC.<br>
                  Visualiza entidades, niveles, tipos y verifica est&aacute;ndares BIM.
                </div>
                <button onclick="document.getElementById(\'fileInput\').click()" style="padding:10px 28px;background:var(--accent);color:#000;border:none;border-radius:5px;font:700 11px var(--mono);text-transform:uppercase;letter-spacing:.12em;cursor:pointer">
                  &#128194; Abrir archivo IFC
                </button>
                <div style="margin-top:14px;font:400 9px var(--mono);color:var(--muted);opacity:.5">
                  Tambi&eacute;n puedes arrastrar un .ifc directamente aqu&iacute;
                </div>
              </div>
            </div>'''
)

# ═══════════════════════════════════════════════════════════════════
# P4 — initViewer: agregar mouse events + initTooltip
# ═══════════════════════════════════════════════════════════════════
patch('P4 initViewer mouse events',
    "  canvas.addEventListener('click',onCanvasClick);\n  window.addEventListener('resize',onResize);",
    "  canvas.addEventListener('click',onCanvasClick);\n"
    "  canvas.addEventListener('mousemove',onCanvasMouseMove);\n"
    "  canvas.addEventListener('mouseleave',hideTooltip);\n"
    "  window.addEventListener('resize',onResize);\n"
    "  initTooltip();"
)

# ═══════════════════════════════════════════════════════════════════
# P5 — limpiarVisor: limpiar globos3d al recargar
# ═══════════════════════════════════════════════════════════════════
patch('P5 limpiarVisor globos',
    '  meshes.forEach(function(m){m.geometry.dispose();m.material.dispose();scene.remove(m)});\n  meshes=[];selectedMesh=null;',
    '  meshes.forEach(function(m){m.geometry.dispose();m.material.dispose();scene.remove(m)});\n'
    '  globos3d.forEach(function(g){g.geometry.dispose();g.material.dispose();scene.remove(g)});\n'
    '  meshes=[];selectedMesh=null;hlActiveCls=null;hlActiveTipo=null;hlActiveNivel=null;globos3d=[];',
    # Reemplaza ambas ocurrencias (en cargarIFC y en limpiarVisor)
)

# Fix P5: necesita reemplazar 2 ocurrencias (cargarIFC + limpiarVisor)
OLD_CLEAN = ('  meshes.forEach(function(m){m.geometry.dispose();m.material.dispose();scene.remove(m)});\n'
             '  meshes=[];selectedMesh=null;')
NEW_CLEAN = ('  meshes.forEach(function(m){m.geometry.dispose();m.material.dispose();scene.remove(m)});\n'
             '  globos3d.forEach(function(g){g.geometry.dispose();g.material.dispose();scene.remove(g)});\n'
             '  meshes=[];selectedMesh=null;hlActiveCls=null;hlActiveTipo=null;hlActiveNivel=null;globos3d=[];')
count = s.count(OLD_CLEAN)
if count == 0:
    if NEW_CLEAN in s:
        ok.append('SKIP P5 limpiarVisor globos')
    else:
        err.append('NOT FOUND P5 limpiarVisor')
else:
    s = s.replace(OLD_CLEAN, NEW_CLEAN)
    ok.append(f'OK   P5 limpiarVisor globos ({count} ocurrencias)')

# ═══════════════════════════════════════════════════════════════════
# P6 — parsearIFC: reemplazar función completa con versión 3 pases
# ═══════════════════════════════════════════════════════════════════
PARSEAR_NEW = '''function parsearIFC(texto){
  var conteo={},instancias={},schema='IFC2X3',proy='\u2014',tiposXClase={};
  var re=/#(\\d+)\\s*=\\s*(IFC[A-Z0-9]+)\\s*\\(/g,m;
  while((m=re.exec(texto))!==null){
    var id=m[1],cls=m[2];
    instancias[id]={cls:cls,pos:m.index+m[0].length};
    conteo[cls]=(conteo[cls]||0)+1;
  }
  var CLASES_TIPO=new Set(['IFCWALL','IFCWALLSTANDARDCASE','IFCCURTAINWALL','IFCSLAB','IFCSLABSTANDARDCASE',
    'IFCCOLUMN','IFCBEAM','IFCFOOTING','IFCPILE','IFCPLATE','IFCMEMBER','IFCDOOR','IFCWINDOW','IFCROOF',
    'IFCSTAIR','IFCRAILING','IFCCOVERING','IFCSPACE','IFCFURNITURE','IFCFURNISHINGELEMENT','IFCSANITARYTERMINAL',
    'IFCPIPESEGMENT','IFCPIPEFITTING','IFCDUCTSEGMENT','IFCDUCTFITTING','IFCPUMP','IFCTANK','IFCVALVE',
    'IFCLIGHTFIXTURE','IFCSENSOR','IFCELECTRICDISTRIBUTIONBOARD','IFCELECTRICAPPLIANCE',
    'IFCFIRESUPPRESSIONTERMINAL','IFCALARM','IFCFLOWMETER','IFCFAN','IFCCOMPRESSOR',
    'IFCUNITARYEQUIPMENT','IFCBOILER','IFCBUILDINGELEMENTPROXY']);
  for(var id in instancias){
    var inst=instancias[id];
    if(!CLASES_TIPO.has(inst.cls))continue;
    var raw=extraerRaw(texto,inst.pos),attrs=splitAttrs(raw);
    var objType=strVal(attrs[4])||strVal(attrs[2])||'(sin tipo)';
    if(!objType||objType==='$')objType='(sin tipo)';
    if(!tiposXClase[inst.cls])tiposXClase[inst.cls]={};
    tiposXClase[inst.cls][objType]=(tiposXClase[inst.cls][objType]||0)+1;
  }
  var elemAStorey={},storeyNombre={};
  for(var id in instancias){
    if(instancias[id].cls==='IFCBUILDINGSTOREY'){
      var raw=extraerRaw(texto,instancias[id].pos),attrs=splitAttrs(raw);
      storeyNombre[id]=strVal(attrs[2])||strVal(attrs[7])||('Nivel #'+id);
    }
  }
  var reRel=/#(\\d+)\\s*=\\s*IFCRELCONTAINEDINSPATIALSTRUCTURE\\s*\\(/g,mr;
  while((mr=reRel.exec(texto))!==null){
    var raw=extraerRaw(texto,mr.index+mr[0].length),attrs=splitAttrs(raw);
    var storeyRef=refId(attrs[5]);if(!storeyRef)continue;
    var lista=attrs[4]||'',reIds=/#(\\d+)/g,mi;
    while((mi=reIds.exec(lista))!==null)elemAStorey[mi[1]]=storeyRef;
  }
  for(var id in instancias){if(elemAStorey[id])instancias[id].storeyId=elemAStorey[id];}
  var tiposXClaseXStorey={};
  for(var id in instancias){
    var inst=instancias[id];if(!CLASES_TIPO.has(inst.cls))continue;
    var raw=extraerRaw(texto,inst.pos),attrs=splitAttrs(raw);
    var objType=strVal(attrs[4])||strVal(attrs[2])||'(sin tipo)';
    if(!objType||objType==='$')objType='(sin tipo)';
    var sId=inst.storeyId||'sin_nivel',sNom=sId!=='sin_nivel'?(storeyNombre[sId]||sId):'Sin nivel';
    if(!tiposXClaseXStorey[inst.cls])tiposXClaseXStorey[inst.cls]={};
    if(!tiposXClaseXStorey[inst.cls][sNom])tiposXClaseXStorey[inst.cls][sNom]={};
    tiposXClaseXStorey[inst.cls][sNom][objType]=(tiposXClaseXStorey[inst.cls][sNom][objType]||0)+1;
  }
  var ms=texto.match(/FILE_SCHEMA\\s*\\(\\s*\\(\\s*'([^']+)'/);if(ms)schema=ms[1];
  var mp=texto.match(/IFCPROJECT\\s*\\([^,]*,[^,]*,\\s*'([^']*)'/);if(mp)proy=mp[1];
  return{conteo:conteo,instancias:instancias,schema:schema,proy:proy,texto:texto,
    tiposXClase:tiposXClase,tiposXClaseXStorey:tiposXClaseXStorey,
    elemAStorey:elemAStorey,storeyNombre:storeyNombre};
}'''

patch_fn('P6 parsearIFC 3 pases', 'parsearIFC', PARSEAR_NEW)

# ═══════════════════════════════════════════════════════════════════
# P7 — verificarNiveles: agregar elevación y orden
# ═══════════════════════════════════════════════════════════════════
patch_fn('P7 verificarNiveles con elevacion', 'verificarNiveles',
'''function verificarNiveles(est){
  var res=[];
  for(var id in est.instancias){
    if(est.instancias[id].cls==='IFCBUILDINGSTOREY'){
      var raw=extraerRaw(est.texto,est.instancias[id].pos),attrs=splitAttrs(raw);
      var nombre=strVal(attrs[2])||strVal(attrs[1])||'';
      var coords=getCoordenadas(est.instancias[id],est.instancias,est.texto);
      var elev=coords?coords.z:null;
      if((elev===null||elev===0)&&attrs[9]){var ea=parseFloat(attrs[9]);if(!isNaN(ea))elev=ea;}
      res.push({id:'#'+id,nombre:nombre,largo:nombre.length,ok:nombre.length===5,elev:elev||0});
    }
  }
  res.sort(function(a,b){return a.elev-b.elev;});
  return res;
}''')

# ═══════════════════════════════════════════════════════════════════
# P8 — Reemplazar bloque "Construir cajas 3D" con versión nueva
# ═══════════════════════════════════════════════════════════════════
BUILD_OLD = '''    /* Construir cajas 3D */
    setLoadText('Construyendo visualización...');
    var categorias=Object.keys(est.conteo).filter(function(c){return c.indexOf('IFC')===0;});
    var totalElems=0,col_idx=0;
    categorias.forEach(function(cls){
      var qty=est.conteo[cls];if(!qty)return;
      totalElems+=qty;
      var col=CAT_COLORS[cls]||CAT_COLORS.DEFAULT;
      var cols_n=Math.ceil(Math.sqrt(Math.min(qty,200)));
      var positions=[],normals=[];
      for(var i=0;i<Math.min(qty,200);i++){
        var row=Math.floor(i/cols_n),c=i%cols_n;
        var geo=new THREE.BoxGeometry(3,0.3+Math.random()*2,3);
        geo.translate(col_idx*12+c*4,0,row*4);
        Array.from(geo.attributes.position.array).forEach(function(v){positions.push(v);});
        Array.from(geo.attributes.normal.array).forEach(function(v){normals.push(v);});
        geo.dispose();
      }
      if(!positions.length)return;
      var mg=new THREE.BufferGeometry();
      mg.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
      mg.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
      var mat=new THREE.MeshLambertMaterial({color:new THREE.Color(col[0],col[1],col[2]),side:THREE.DoubleSide});
      var mesh=new THREE.Mesh(mg,mat);
      mesh.userData={cls:cls,qty:qty,baseColor:new THREE.Color(col[0],col[1],col[2])};
      scene.add(mesh);meshes.push(mesh);col_idx++;
    });'''

BUILD_NEW = '''    /* Construir cajas 3D: cuadricula XY centrada, Z por storey */
    setLoadText('Construyendo visualizaci\u00f3n...');
    var FORMA={
      IFCWALL:{w:0.4,h:3.0,d:4.0},IFCWALLSTANDARDCASE:{w:0.4,h:3.0,d:4.0},
      IFCCURTAINWALL:{w:0.2,h:3.2,d:4.0},IFCSLAB:{w:4.0,h:0.3,d:4.0},
      IFCSLABSTANDARDCASE:{w:4.0,h:0.3,d:4.0},IFCROOF:{w:4.0,h:0.4,d:4.0},
      IFCCOLUMN:{w:0.6,h:3.5,d:0.6},IFCBEAM:{w:4.0,h:0.5,d:0.5},
      IFCFOOTING:{w:2.0,h:0.5,d:2.0},IFCDOOR:{w:1.2,h:2.4,d:0.2},
      IFCWINDOW:{w:1.4,h:1.2,d:0.15},IFCSTAIR:{w:2.0,h:2.0,d:2.0},
      IFCRAILING:{w:3.0,h:1.0,d:0.1},IFCCOVERING:{w:3.0,h:0.05,d:3.0},
      IFCSPACE:{w:4.0,h:2.8,d:4.0},IFCPIPESEGMENT:{w:3.0,h:0.2,d:0.2},
      IFCPIPEFITTING:{w:0.4,h:0.4,d:0.4},IFCDUCTSEGMENT:{w:3.0,h:0.4,d:0.6},
      IFCDUCTFITTING:{w:0.7,h:0.5,d:0.7},IFCPUMP:{w:1.0,h:1.0,d:1.0},
      IFCTANK:{w:1.5,h:2.0,d:1.5},IFCVALVE:{w:0.4,h:0.4,d:0.4},
      IFCLIGHTFIXTURE:{w:0.6,h:0.15,d:0.6},IFCSENSOR:{w:0.2,h:0.2,d:0.1},
      IFCELECTRICDISTRIBUTIONBOARD:{w:0.8,h:1.2,d:0.2},
      IFCFURNITURE:{w:1.5,h:1.0,d:1.5},IFCFURNISHINGELEMENT:{w:1.5,h:1.0,d:1.5},
      IFCSANITARYTERMINAL:{w:0.7,h:0.6,d:0.5},IFCFIRESUPPRESSIONTERMINAL:{w:0.3,h:0.5,d:0.3},
      IFCALARM:{w:0.2,h:0.2,d:0.1},IFCBUILDINGELEMENTPROXY:{w:1.0,h:1.0,d:1.0},
      DEFAULT:{w:1.5,h:1.5,d:1.5}
    };
    var totalElems=0;
    var CLASES_RENDER=new Set(Object.keys(FORMA).filter(function(k){return k!=='DEFAULT';}));
    var todasClases=Object.keys(est.conteo).filter(function(c){return CLASES_RENDER.has(c)&&est.conteo[c]>0;});
    var storeysOrdenados=verificarNiveles(est).map(function(n){return n.nombre;});
    var nCls=todasClases.length,nCols=Math.ceil(Math.sqrt(nCls)),nRows=Math.ceil(nCls/nCols),CELL=22;
    todasClases.forEach(function(cls,ci){
      var qty=est.conteo[cls];if(!qty)return;
      var col=CAT_COLORS[cls]||CAT_COLORS.DEFAULT,forma=FORMA[cls]||FORMA.DEFAULT;
      var gx=(ci%nCols)-(nCols-1)/2,gy=Math.floor(ci/nCols)-(nRows-1)/2;
      var baseX=gx*CELL,baseZ=gy*CELL;
      var txcs=est.tiposXClaseXStorey&&est.tiposXClaseXStorey[cls];
      if(txcs){
        storeysOrdenados.forEach(function(storeyNom,si){
          if(!txcs[storeyNom])return;
          var storeyY=si*12;
          var tiposDeStorey=Object.keys(txcs[storeyNom]);
          var tCols=Math.ceil(Math.sqrt(Math.min(tiposDeStorey.length,16)));
          tiposDeStorey.forEach(function(tipo,ti){
            var tqty=txcs[storeyNom][tipo];totalElems+=tqty;
            var tx=(ti%tCols-(tCols-1)/2)*(forma.w+0.8);
            var tz=Math.floor(ti/tCols)*(forma.d+0.8);
            var nBoxes=Math.min(tqty,16),bCols=Math.ceil(Math.sqrt(nBoxes));
            var positions=[],normals=[];
            for(var i=0;i<nBoxes;i++){
              var br=Math.floor(i/bCols),bc=i%bCols;
              var geo=new THREE.BoxGeometry(forma.w,forma.h,forma.d);
              geo.translate(baseX+tx+bc*(forma.w+0.3),storeyY+forma.h/2,baseZ+tz+br*(forma.d+0.3));
              Array.from(geo.attributes.position.array).forEach(function(v){positions.push(v);});
              Array.from(geo.attributes.normal.array).forEach(function(v){normals.push(v);});
              geo.dispose();
            }
            if(!positions.length)return;
            var mg=new THREE.BufferGeometry();
            mg.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
            mg.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
            var mat=new THREE.MeshLambertMaterial({color:new THREE.Color(col[0],col[1],col[2]),side:THREE.DoubleSide});
            var mesh=new THREE.Mesh(mg,mat);
            mg.computeBoundingBox();var bb=mg.boundingBox;
            mesh.userData={cls:cls,tipo:tipo,storeyNom:storeyNom,qty:tqty,
              baseColor:new THREE.Color(col[0],col[1],col[2]),yMin:bb?bb.min.y:0,yMax:bb?bb.max.y:0};
            scene.add(mesh);meshes.push(mesh);
          });
        });
      } else {
        totalElems+=qty;
        var cols_n=Math.ceil(Math.sqrt(Math.min(qty,64))),positions=[],normals=[];
        for(var i=0;i<Math.min(qty,64);i++){
          var row=Math.floor(i/cols_n),c2=i%cols_n;
          var geo=new THREE.BoxGeometry(forma.w,forma.h,forma.d);
          geo.translate(baseX+c2*(forma.w+0.5),forma.h/2,baseZ+row*(forma.d+0.5));
          Array.from(geo.attributes.position.array).forEach(function(v){positions.push(v);});
          Array.from(geo.attributes.normal.array).forEach(function(v){normals.push(v);});
          geo.dispose();
        }
        if(!positions.length)return;
        var mg=new THREE.BufferGeometry();
        mg.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
        mg.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
        var mat=new THREE.MeshLambertMaterial({color:new THREE.Color(col[0],col[1],col[2]),side:THREE.DoubleSide});
        var mesh=new THREE.Mesh(mg,mat);
        mg.computeBoundingBox();var bb=mg.boundingBox;
        mesh.userData={cls:cls,tipo:null,storeyNom:null,qty:qty,
          baseColor:new THREE.Color(col[0],col[1],col[2]),yMin:bb?bb.min.y:0,yMax:bb?bb.max.y:0};
        scene.add(mesh);meshes.push(mesh);
      }
    });
    /* Elipsoides por clase */
    todasClases.forEach(function(cls){
      var mc=meshes.filter(function(m){return m.userData.cls===cls;});if(!mc.length)return;
      var bbox=new THREE.Box3();mc.forEach(function(m){bbox.expandByObject(m);});
      var center=bbox.getCenter(new THREE.Vector3()),size=bbox.getSize(new THREE.Vector3());
      var col=CAT_COLORS[cls]||CAT_COLORS.DEFAULT;
      var nomCls=ESP_ENTS.reduce(function(a,e){return e[0]===cls?e[1]:a;},'')
                 ||cls.charAt(0)+cls.slice(1).toLowerCase();
      [false,true].forEach(function(wire){
        var geo=new THREE.SphereGeometry(1,16,12);
        var mat=wire
          ?new THREE.MeshBasicMaterial({color:new THREE.Color(col[0],col[1],col[2]),wireframe:true,transparent:true,opacity:0.08,depthWrite:false})
          :new THREE.MeshLambertMaterial({color:new THREE.Color(col[0],col[1],col[2]),transparent:true,opacity:0.06,side:THREE.BackSide,depthWrite:false});
        var g=new THREE.Mesh(geo,mat);
        g.position.copy(center);
        g.scale.set(size.x*0.55+2.5,size.y*0.55+2.5,size.z*0.55+2.5);
        g.userData={esGlobo:true,cls:cls,label:nomCls,total:est.conteo[cls]||0};
        scene.add(g);globos3d.push(g);
      });
    });'''

patch('P8 construir cajas XY+Z+elipsoides', BUILD_OLD, BUILD_NEW)

# ═══════════════════════════════════════════════════════════════════
# P9 — Insertar tooltip JS + highlight functions antes de CONTROLES 3D
# ═══════════════════════════════════════════════════════════════════
TOOLTIP_JS = '''/* ═══ TOOLTIP 3D ═══ */
var ttEl,ttCls,ttNom,ttSub;
function initTooltip(){
  ttEl=document.getElementById('tooltip3d');
  ttCls=document.getElementById('ttCls');
  ttNom=document.getElementById('ttNom');
  ttSub=document.getElementById('ttSub');
}
function showTooltip(e,m){
  var ud=m.userData;
  ttCls.textContent=ud.cls||'';
  ttNom.textContent=ud.tipo||ud.label||'';
  ttSub.textContent=ud.storeyNom?(ud.storeyNom+' \u00b7 '+ud.qty+' ud.'):(ud.total?ud.total+' elementos':'');
  ttEl.style.display='block';posTooltip(e);
}
function posTooltip(e){
  var x=e.clientX+14,y=e.clientY-10;
  if(x+180>window.innerWidth)x=e.clientX-190;
  ttEl.style.left=x+'px';ttEl.style.top=y+'px';
}
function hideTooltip(){if(ttEl)ttEl.style.display='none';}
function onCanvasMouseMove(e){
  if(!renderer3)return;
  var rect=renderer3.domElement.getBoundingClientRect();
  mouse.x=((e.clientX-rect.left)/rect.width)*2-1;
  mouse.y=-((e.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(mouse,camera);
  var hitsM=raycaster.intersectObjects(meshes).filter(function(h){return !h.object.userData.esGlobo;});
  if(hitsM.length){showTooltip(e,hitsM[0].object);return;}
  var hitsG=raycaster.intersectObjects(globos3d);
  if(hitsG.length&&hitsG[0].object.userData.esGlobo){showTooltip(e,hitsG[0].object);return;}
  hideTooltip();
}

/* ═══ HIGHLIGHT 3D DESDE REPORTE ═══ */
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
}
function hlSelectTipoElem(e,cls,tipo){
  e.stopPropagation();
  if(hlActiveCls===cls&&hlActiveTipo===tipo){hlClear();return;}
  hlActiveCls=cls;hlActiveTipo=tipo;hlActiveNivel=null;
  var target=null;
  meshes.forEach(function(m){
    var match=m.userData.cls===cls&&m.userData.tipo===tipo;
    if(match){m.material.color.set(0x00d4ff);m.material.transparent=false;m.material.opacity=1;target=m;}
    else{m.material.color.set(0x1a2a40);m.material.transparent=true;m.material.opacity=0.18;}
  });
  document.querySelectorAll('.rp-tipo-item').forEach(function(el){
    el.classList.toggle('hl-active',el.dataset.cls===cls&&el.dataset.tipo===tipo);
  });
  if(target){
    var bbox=new THREE.Box3().setFromObject(target),center=bbox.getCenter(new THREE.Vector3()),size=bbox.getSize(new THREE.Vector3()).length();
    controls.target.copy(center);camera.position.set(center.x+size*.7,center.y+size*.5,center.z+size*.7);controls.update();
  }
}
function hlSelectNivel(idx,niveles){
  if(hlActiveNivel===idx){hlClear();return;}
  hlActiveNivel=idx;hlActiveCls=null;hlActiveTipo=null;
  var storeyNom=niveles[idx].nombre;
  meshes.forEach(function(m){
    if(m.userData.storeyNom===storeyNom){m.material.color.set(0x00d4ff);m.material.transparent=false;m.material.opacity=1;}
    else{m.material.color.set(0x1a2a40);m.material.transparent=true;m.material.opacity=0.12;}
  });
  document.querySelectorAll('.rp-nivel-item').forEach(function(el){
    el.classList.toggle('hl-active',parseInt(el.dataset.idx)===idx);
  });
  var bbox=new THREE.Box3(),found=false;
  meshes.forEach(function(m){if(m.userData.storeyNom===storeyNom){bbox.expandByObject(m);found=true;}});
  if(found){
    var center=bbox.getCenter(new THREE.Vector3()),size=bbox.getSize(new THREE.Vector3()).length();
    controls.target.copy(center);camera.position.set(center.x+size*.7,center.y+size*.5,center.z+size*.7);controls.update();
  }
}
function hlClear(){
  hlActiveCls=null;hlActiveTipo=null;hlActiveNivel=null;
  meshes.forEach(function(m){m.material.color.copy(m.userData.baseColor);m.material.transparent=ghostMode;m.material.opacity=ghostMode?0.3:1;});
  document.querySelectorAll('.rp-tipo-item.hl-active,.rp-nivel-item.hl-active').forEach(function(el){el.classList.remove('hl-active');});
}
'''

patch('P9 tooltip+highlight JS',
    '/* ═══ CONTROLES 3D ═══ */',
    TOOLTIP_JS + '/* ═══ CONTROLES 3D ═══ */'
)

# ═══════════════════════════════════════════════════════════════════
# P10 — renderReporte: reemplazar función completa con versión 5 secciones
# ═══════════════════════════════════════════════════════════════════
REPORTE_NEW = '''/* ═══ RENDER REPORTE ═══ */
function rpSec(title,badge,bc,body,open){
  var uid='rps'+Math.random().toString(36).substr(2,5);
  return '<div class="rp-sec">'+
    '<div class="rp-sec-hdr" onclick="rpToggle(\''+uid+'\')">'+
    '<span class="rp-sec-title">'+title+'</span>'+
    '<span class="rp-badge '+bc+'">'+badge+'</span>'+
    '&nbsp;<span class="rp-arr" id="a_'+uid+'">'+(open?'&#9662;':'&#9658;')+'</span>'+
    '</div>'+
    '<div class="rp-content" id="'+uid+'" style="'+(open?'':'display:none')+'">'+body+'</div>'+
    '</div>';
}
function rpToggle(uid){
  var el=document.getElementById(uid),ar=document.getElementById('a_'+uid);
  var open=el.style.display==='none';
  el.style.display=open?'':'none';ar.innerHTML=open?'&#9662;':'&#9658;';
}
function tipoGrupoToggle(uid){
  var el=document.getElementById(uid),ar=document.getElementById('ar_'+uid);
  var open=el.style.display==='none'||!el.style.display;
  document.querySelectorAll('.rp-tipo-items').forEach(function(x){x.style.display='none';});
  document.querySelectorAll('.rp-tipo-grupo-arr').forEach(function(x){x.classList.remove('open');});
  if(open){el.style.display='block';ar.classList.add('open');}
}
function renderTiposElemento(tiposXClase){
  if(!tiposXClase||!Object.keys(tiposXClase).length)return '<div class="rp-msg">Sin tipos detectados.</div>';
  var html='<div class="rp-hl-hint">&#9658; Clic para resaltar en 3D</div>';
  Object.keys(tiposXClase).sort().forEach(function(cls,ci){
    var tipos=tiposXClase[cls],tiposOrd=Object.keys(tipos).sort(function(a,b){return tipos[b]-tipos[a];});
    var total=tiposOrd.reduce(function(s,t){return s+tipos[t];},0);
    var uid='te'+ci+'_'+Math.random().toString(36).substr(2,4);
    var nomCls=ESP_ENTS.reduce(function(a,e){return e[0]===cls?e[1]:a;},'')
               ||cls.charAt(0)+cls.slice(1).toLowerCase();
    var col=CAT_COLORS[cls]||CAT_COLORS.DEFAULT;
    var dot='rgb('+(col.map(function(v){return Math.round(v*255);})).join(',')+')';
    var items=tiposOrd.map(function(tipo){
      var qty=tipos[tipo];
      var tipoEsc=tipo.replace(/'/g,"\\'").replace(/"/g,'&quot;');
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
        '<span class="rp-tipo-grupo-count">'+total+'</span>'+
        '<span class="rp-tipo-grupo-arr" id="ar_'+uid+'">&#9658;</span>'+
      '</div>'+
      '<div class="rp-tipo-items" id="'+uid+'">'+items+'</div></div>';
  });
  return html;
}
function renderReporte(est){
  var html='',co=est.conteo;
  /* 1 Origen */
  var orig=verificarOrigen(est);
  if(orig.length){
    var ok2=orig.every(function(r){return r.ok;});
    var rows=orig.map(function(r){
      var coords=r.x!==null?'('+[r.x,r.y,r.z].map(function(v){return(+v).toFixed(3);}).join(', ')+')':'N/A';
      return '<tr><td class="td-name">'+r.tipo.charAt(0)+r.tipo.slice(1).toLowerCase()+
        '<div class="td-cls">'+esc(r.nombre)+'</div></td>'+
        '<td style="font:400 9px var(--mono);color:var(--muted)">'+coords+'</td>'+
        '<td class="td-ok">'+(r.ok?'<span class="ic-ok">&#10003;</span>':'<span class="ic-err">&#10007;</span>')+'</td></tr>';
    }).join('');
    html+=rpSec('Origen (0,0,0)',ok2?'OK':'Error',ok2?'rp-ok':'rp-err','<table class="rp-table">'+rows+'</table>',!ok2);
  }
  /* 2 Nombres */
  var noms=verificarNombres(est);
  if(noms.length){
    var ok2=noms.every(function(r){return r.ok;});
    var rows=noms.map(function(r){
      return '<tr><td class="td-name">'+r.tipo.charAt(0)+r.tipo.slice(1).toLowerCase()+'</td>'+
        '<td>"'+esc(r.nombre)+'" ('+r.largo+' car.)</td>'+
        '<td class="td-ok">'+(r.ok?'<span class="ic-ok">&#10003;</span>':'<span class="ic-err">&#10007;</span>')+'</td></tr>';
    }).join('');
    html+=rpSec('Nombres Sitio/Edificio',ok2?'OK':'Error',ok2?'rp-ok':'rp-err',
      '<div class="rp-msg">Sitio: 3 car. &middot; Edificio: 2 car.</div><table class="rp-table">'+rows+'</table>',!ok2);
  }
  /* 3 Niveles */
  var nivs=verificarNiveles(est);
  if(nivs.length){
    var nOk=nivs.filter(function(r){return r.ok;}).length;
    var nivsHtml=nivs.map(function(r,idx){
      var elev=typeof r.elev==='number'?r.elev.toFixed(2)+'m':'?';
      var badge=r.ok?'<span class="rp-nivel-item-badge badge-ok">5 car.</span>':'<span class="rp-nivel-item-badge badge-warn">'+r.largo+' car.</span>';
      return '<div class="rp-nivel-item" data-idx="'+idx+'" onclick="hlSelectNivel('+idx+','+JSON.stringify(nivs)+')">'+
        '<div style="flex:1;min-width:0"><div class="rp-nivel-item-name">'+esc(r.nombre||'(sin nombre)')+'</div>'+
        '<div class="rp-nivel-item-sub">z = '+elev+'</div></div>'+badge+'</div>';
    }).join('');
    html+=rpSec('Niveles (5 car.)',nOk+'/'+nivs.length+' OK',nOk===nivs.length?'rp-ok':nOk>0?'rp-warn':'rp-err',nivsHtml,true);
  }
  /* 4 Entidades */
  var filas='',pres=0;
  ESP_ENTS.forEach(function(e){
    var cls=e[0],nom=e[1],qty=co[cls]||0;if(qty>0)pres++;
    var hm=meshes.some(function(m){return m.userData.cls===cls;});
    var tr=hm?' class="has-mesh" onclick="hlSelect(\''+cls+'\')"':'';
    filas+='<tr'+tr+'><td class="td-name">'+nom+'<div class="td-cls">'+cls.charAt(0)+cls.slice(1).toLowerCase()+'</div></td>'+
      '<td class="td-qty'+(qty===0?' zero':'')+'">'+qty+'</td>'+
      '<td class="td-ok">'+(qty>0?'<span class="ic-ok">&#10003;</span>':'<span class="ic-err">&#10007;</span>')+'</td></tr>';
  });
  var pct=ESP_ENTS.length?Math.round(pres/ESP_ENTS.length*100):0;
  html+=rpSec('Entidades IFC',pres+'/'+ESP_ENTS.length,pct===100?'rp-ok':pct>50?'rp-warn':'rp-err',
    '<div class="rp-hl-hint">&#9658; Clic en fila para resaltar en 3D</div><table class="rp-table">'+filas+'</table>',false);
  /* 5 Tipos */
  if(est.tiposXClase&&Object.keys(est.tiposXClase).length)
    html+=rpSec('Tipos de Elementos','familias','rp-info',renderTiposElemento(est.tiposXClase),false);
  document.getElementById('rpBody').innerHTML=html;
}
'''

# Reemplazar usando patch_fn para el bloque completo
idx = s.find('/* ═══ RENDER REPORTE ═══ */')
if idx == -1:
    err.append('NOT FOUND: bloque RENDER REPORTE')
else:
    end = s.find('\n/* ═══ CARGA IFC ═══ */', idx)
    if end == -1:
        err.append('NOT FOUND: fin RENDER REPORTE')
    elif 'renderTiposElemento' in s[idx:end]:
        ok.append('SKIP P10 renderReporte (ya completo)')
    else:
        s = s[:idx] + REPORTE_NEW + s[end:]
        ok.append('OK   P10 renderReporte 5 secciones')

# ═══════════════════════════════════════════════════════════════════
# VERIFICACION FINAL + GUARDAR
# ═══════════════════════════════════════════════════════════════════
print()
print('=== Log de patches ===')
for msg in ok: print(' ', msg)
if err:
    print()
    print('=== ERRORES ===')
    for msg in err: print('  !!', msg)

checks = {
    'P1  globos3d':        'globos3d' in s,
    'P2  CSS tooltip':     '#tooltip3d{' in s,
    'P3a tooltip div':     'id="tooltip3d"' in s,
    'P3b ovWelcome':       'Abrir archivo IFC' in s,
    'P4  mouse events':    'onCanvasMouseMove' in s,
    'P5  limpiar globos':  'globos3d.forEach' in s,
    'P6  parsearIFC':      'tiposXClaseXStorey' in s,
    'P7  niveles elev':    'elev:elev||0' in s,
    'P8  FORMA':           'var FORMA=' in s,
    'P8  elipsoides':      'esGlobo:true' in s,
    'P9  hlSelect':        'function hlSelect(' in s,
    'P9  hlSelectNivel':   'function hlSelectNivel(' in s,
    'P10 renderReporte':   'renderTiposElemento' in s,
    'P10 5 secciones':     'Tipos de Elementos' in s,
    'UTF-8 limpio':        '\ufffd' not in s and 'â€' not in s,
}
print()
print('=== Verificacion ===')
all_ok = True
for k,v in checks.items():
    status = 'OK  ' if v else 'FAIL'
    if not v: all_ok = False
    print(f'  {status} {k}')

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(s)

print()
lines = s.count('\n')
print(f'Guardado: {SRC}')
print(f'Lineas: {lines}')
print(f'Estado: {"TODO OK" if all_ok and not err else "HAY PROBLEMAS"}')
