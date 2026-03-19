const fs = require('fs');
let s = fs.readFileSync('C:/Users/Usuario/Documents/GitHub/Revisor-IFC/explorer.html', 'utf8');

// ── FIX 1: Estado global — agregar globos3d ──────────────────────────────────
s = s.replace(
  'var meshes = [], selectedMesh = null;',
  'var meshes = [], selectedMesh = null, globos3d = [];\nvar hlActiveCls = null, hlActiveTipo = null, hlActiveNivel = null;'
);

// ── FIX 2: initViewer — agregar tooltip, mousemove, mouseleave ───────────────
s = s.replace(
  '  canvas.addEventListener(\'click\',onCanvasClick);\n  window.addEventListener(\'resize\',onResize);',
  '  canvas.addEventListener(\'click\',onCanvasClick);\n  canvas.addEventListener(\'mousemove\',onCanvasMouseMove);\n  canvas.addEventListener(\'mouseleave\',hideTooltip);\n  window.addEventListener(\'resize\',onResize);\n  initTooltip();'
);

// ── FIX 3: parsearIFC — reemplazar version simple por version completa ────────
const parsearOld = `function parsearIFC(texto){
  var conteo={},instancias={},schema='IFC2X3',proy='—';
  var re=/#(\\d+)\\s*=\\s*(IFC[A-Z0-9]+)\\s*\\(/g,m;
  while((m=re.exec(texto))!==null){
    var id=m[1],cls=m[2];
    instancias[id]={cls:cls,pos:m.index+m[0].length};
    conteo[cls]=(conteo[cls]||0)+1;
  }
  var ms=texto.match(/FILE_SCHEMA\\s*\\(\\s*\\(\\s*'([^']+)'/);if(ms)schema=ms[1];
  var mp=texto.match(/IFCPROJECT\\s*\\([^,]*,[^,]*,\\s*'([^']*)'/);if(mp)proy=mp[1];
  return{conteo:conteo,instancias:instancias,schema:schema,proy:proy,texto:texto};
}`;

const parsearNew = `function parsearIFC(texto){
  var conteo={},instancias={},schema='IFC2X3',proy='—';
  var tiposXClase={};
  var re=/#(\\d+)\\s*=\\s*(IFC[A-Z0-9]+)\\s*\\(/g,m;
  while((m=re.exec(texto))!==null){
    var id=m[1],cls=m[2];
    instancias[id]={cls:cls,pos:m.index+m[0].length};
    conteo[cls]=(conteo[cls]||0)+1;
  }
  var CLASES_TIPO=new Set(['IFCWALL','IFCWALLSTANDARDCASE','IFCCURTAINWALL','IFCSLAB','IFCSLABSTANDARDCASE','IFCCOLUMN','IFCBEAM','IFCFOOTING','IFCPILE','IFCPLATE','IFCMEMBER','IFCDOOR','IFCWINDOW','IFCROOF','IFCSTAIR','IFCRAILING','IFCCOVERING','IFCSPACE','IFCFURNITURE','IFCFURNISHINGELEMENT','IFCSANITARYTERMINAL','IFCPIPESEGMENT','IFCPIPEFITTING','IFCDUCTSEGMENT','IFCDUCTFITTING','IFCPUMP','IFCTANK','IFCVALVE','IFCLIGHTFIXTURE','IFCSENSOR','IFCELECTRICDISTRIBUTIONBOARD','IFCELECTRICAPPLIANCE','IFCFIRESUPPRESSIONTERMINAL','IFCALARM','IFCFLOWMETER','IFCFAN','IFCCOMPRESSOR','IFCUNITARYEQUIPMENT','IFCBOILER','IFCBUILDINGELEMENTPROXY']);
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
}`;

s = s.replace(parsearOld, parsearNew);

// ── FIX 4: verificarNiveles — agregar elevación ───────────────────────────────
s = s.replace(
  `      res.push({id:'#'+id,nombre:nombre,largo:nombre.length,ok:nombre.length===5});`,
  `      var coords=getCoordenadas(instancias[id],instancias,texto);
      var elev=coords?coords.z:null;
      if((elev===null||elev===0)&&attrs[9]){var ea=parseFloat(attrs[9]);if(!isNaN(ea))elev=ea;}
      res.push({id:'#'+id,nombre:nombre,largo:nombre.length,ok:nombre.length===5,elev:elev||0});`
);
s = s.replace(
  `  return res;\n}`,
  `  res.sort(function(a,b){return a.elev-b.elev;});\n  return res;\n}`
);

console.log('Checks:\n  globos3d:', s.includes('globos3d'),
  '\n  tiposXClaseXStorey:', s.includes('tiposXClaseXStorey'),
  '\n  storeyNombre:', s.includes('storeyNombre'),
  '\n  elev:', s.includes('elev:elev||0'));

fs.writeFileSync('C:/Users/Usuario/Documents/GitHub/Revisor-IFC/explorer.html', s, 'utf8');
console.log('Paso 1 OK — lineas:', s.split('\n').length);
