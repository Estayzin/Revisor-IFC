const fs = require('fs');
let s = fs.readFileSync('C:/Users/Usuario/Documents/GitHub/Revisor-IFC/explorer.html', 'utf8');

// Reemplazar parsearIFC completo usando marcadores de inicio/fin
const start = s.indexOf('function parsearIFC(texto){');
const end = s.indexOf('\n}\n', start) + 3;

if(start === -1 || end < start){ console.error('No encontró parsearIFC'); process.exit(1); }

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
}
`;

s = s.slice(0, start) + parsearNew + s.slice(end);

console.log('tiposXClaseXStorey:', s.includes('tiposXClaseXStorey'));
console.log('storeyNombre:', s.includes('storeyNombre'));
fs.writeFileSync('C:/Users/Usuario/Documents/GitHub/Revisor-IFC/explorer.html', s, 'utf8');
console.log('Paso 2 OK — lineas:', s.split('\n').length);
