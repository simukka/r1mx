class GUI.GPDB.GPdbSocket extends XMLSocket
{
   var onConnect;
   var onData;
   var onXML;
   var onClose;
   var __closeRequested = false;
   var __socAddr = null;
   var __socPort = null;
   var __gpdbxml = null;
   var __nConnectionAttempts = 0;
   function GPdbSocket(socAddr, socPort, gpdbXml, connectFnc)
   {
      super();
      this.__gpdbxml = gpdbXml;
      _global.VxDebug("...........................................................................CTOR GPdbSocket()");
      if(gpdbXml)
      {
      }
      this.onConnect = function(connectionStatus)
      {
         var _loc2_ = connectFnc;
         if(connectionStatus == true)
         {
            _loc2_();
         }
         else
         {
            this.attemptConnectToXmlServer();
         }
      };
      this.onData = function(src)
      {
         this.__gpdbxml.parseXML(src);
         this.__gpdbxml.parseSnippet();
      };
      this.onXML = function(src)
      {
      };
      this.onClose = function(src)
      {
         if("SHUTDOWN" != _global.gpdb.paramGet("SYSTEM.RUNLEVEL.REQUESTED"))
         {
            _global.log("GPdbSocket.onClose(): envoked! Yikes! This should not happen under normal usage!");
         }
         if(!this.__closeRequested)
         {
         }
      };
      if(socAddr != null)
      {
         if(socPort != null)
         {
            this.__socAddr = socAddr;
            this.__socPort = Number(socPort);
            this.attemptConnectToXmlServer();
         }
      }
   }
   function attemptConnectToXmlServer()
   {
      var _loc2_ = 3;
      if(++this.__nConnectionAttempts <= _loc2_)
      {
         this.connect(this.__socAddr,this.__socPort);
      }
   }
   function sendParam(name, type, value)
   {
      var _loc3_ = new XML();
      var _loc2_ = _loc3_.createElement("Param");
      _loc2_.attributes.value = value;
      _loc2_.attributes.type = type;
      _loc2_.attributes.name = name;
      _loc3_.appendChild(_loc2_);
      this.send(_loc3_);
   }
   function sendCmd(name, arg)
   {
      var _loc3_ = new XML();
      var _loc2_ = _loc3_.createElement("Cmnd");
      _loc2_.attributes.arg = arg;
      _loc2_.attributes.name = name;
      _loc3_.appendChild(_loc2_);
      this.send(_loc3_);
   }
}
