class GUI.GPDB.GPDBLocal extends GUI.GPDB.GPDBConnection
{
   var __connectID;
   var __fname;
   var __lc;
   var __xmlParser;
   static var LC_NAME = "_GPDB_";
   static var MAX_CONNECT = 50;
   var __queue = [];
   var __processing = false;
   function GPDBLocal(gpdb)
   {
      super();
      _global.VxDebug("...........................................................................CTOR GPDBLocal()");
      this.__xmlParser = new GUI.GPDB.GPdbXml(gpdb);
      this.__lc = new LocalConnection();
      var _loc0_;
      var _loc5_ = this.__fname = _root._url.substr(_root._url.lastIndexOf("/") + 1);
      this.__lc.receiveXML = mx.utils.Delegate.create(this,this.CB_ReceiveXML);
      this.__lc.receiveCmd = mx.utils.Delegate.create(this,this.CB_ReceiveCmd);
      this.__lc.onStatus = mx.utils.Delegate.create(this,this.CB_onStatus);
      this.__lc.allowDomain = mx.utils.Delegate.create(this,this.CB_allowDomain);
      this.SelfAssignID();
   }
   function SelfAssignID()
   {
      var _loc2_ = 0;
      var _loc3_ = false;
      _loc2_ = 0;
      while(_loc2_ < GUI.GPDB.GPDBLocal.MAX_CONNECT)
      {
         this.__connectID = GUI.GPDB.GPDBLocal.LC_NAME + _loc2_;
         _loc3_ = this.__lc.connect(this.__connectID);
         if(_loc3_)
         {
            break;
         }
         _loc2_ = _loc2_ + 1;
      }
      if(!_loc3_)
      {
         this.__connectID = undefined;
         this.__lc.close();
         throw new Error("GPDBLocal::SelfAssignID(" + this.__fname + ") unable to find an available connection ID.");
      }
   }
   function CB_ReceiveXML(xml)
   {
      this.__xmlParser.parseXML(xml);
      this.__xmlParser.parseSnippet();
   }
   function CB_ReceiveCmd(cmd, arg)
   {
      if(this.__processing)
      {
         this.__queue.push({name:cmd,arg:arg});
      }
      else
      {
         this.startProcessing();
         cmd = cmd.toUpperCase();
         switch(cmd)
         {
            case "SYNC":
               this.__xmlParser.parseXML("<Sync id=\"" + arg + "\"/>");
               this.__xmlParser.parseSnippet();
               this.endProcessing();
               return;
            case "GET_PARAM":
               if(arg == "*")
               {
                  this.__xmlParser.parseXML("<RedParameters></RedParameters>");
                  this.__xmlParser.parseSnippet();
                  this.endProcessing();
               }
               return;
            case "GET_FILE":
               this.__xmlParser.addEventListener("EVENT_FACTORY_DEFAULTS_REGISTERED",mx.utils.Delegate.create(this,this.endProcessing));
               this.__xmlParser.load(arg);
               return;
            default:
               this.endProcessing();
               return;
         }
      }
   }
   function CB_onStatus(infoObj)
   {
   }
   function CB_allowDomain(sendingDomain)
   {
      return true;
   }
   function startProcessing()
   {
      this.__processing = true;
   }
   function endProcessing()
   {
      this.__processing = false;
      var _loc2_;
      if(this.__queue.length > 0)
      {
         _loc2_ = this.__queue.shift();
         this.__lc.receiveCmd(_loc2_.name,_loc2_.arg);
      }
   }
   function sendParam(param)
   {
      var _loc3_ = "<Param name=\"" + param.name + "\" type=\"" + param.type + "\" value=\"" + param.value + "\"/>";
      var _loc2_ = 0;
      var _loc4_;
      var _loc5_ = new LocalConnection();
      _loc2_ = 0;
      while(_loc2_ < GUI.GPDB.GPDBLocal.MAX_CONNECT)
      {
         _loc4_ = !_loc5_.connect(GUI.GPDB.GPDBLocal.LC_NAME + _loc2_);
         if(!_loc4_)
         {
            break;
         }
         if(!(_loc2_ > 0 && _loc2_ == this.__connectID))
         {
            if(this.__lc.send(GUI.GPDB.GPDBLocal.LC_NAME + _loc2_,"receiveXML",_loc3_))
            {
            }
         }
         _loc2_ = _loc2_ + 1;
      }
      _loc5_.close();
   }
   function sendCmd(fncName, arg)
   {
      if(this.__lc.send(this.__connectID,"receiveCmd",fncName,arg))
      {
      }
   }
   function sync(fnc, syncEventName)
   {
      this.__xmlParser.addEventListener(syncEventName,fnc);
   }
}
