class GUI.GPDB.GPDBCamera extends GUI.GPDB.GPDBConnection
{
   var __xml;
   var __socket;
   static var XML_SERVER_PORT = "49152";
   function GPDBCamera(gpdb, goFunc, addr)
   {
      super();
      _global.VxDebug("...........................................................................CTOR GPDBCamera()");
      this.__xml = new GUI.GPDB.GPdbXml(gpdb);
      this.__socket = new GUI.GPDB.GPdbSocket(addr,GUI.GPDB.GPDBCamera.XML_SERVER_PORT,this.__xml,goFunc);
   }
   function sendParam(param)
   {
      this.__socket.sendParam(param.name,param.type,param.value);
   }
   function sendCmd(fncName, arg)
   {
      this.__socket.sendCmd(fncName,arg);
   }
   function sync(fnc, syncEventName)
   {
      this.__xml.addEventListener(syncEventName,fnc);
   }
}
