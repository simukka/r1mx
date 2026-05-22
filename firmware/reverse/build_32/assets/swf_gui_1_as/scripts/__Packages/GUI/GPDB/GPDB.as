class GUI.GPDB.GPDB
{
   var __gpdb;
   var __goFnc;
   var __GuiBoot1;
   var __GuiBoot2;
   var __GuiBoot3;
   var __onReadyCallbacks;
   var __connection;
   var __globalCallbacklist;
   static var __paramDB;
   static var LOCALHOST = "127.0.0.1";
   var __isActive = false;
   var __dirty = false;
   var __syncNum = 0;
   var __callbacksEnabled = false;
   var __autoXmit = true;
   function GPDB(goFnc, ipAddr)
   {
      var _loc6_ = undefined;
      var _loc7_ = undefined;
      var _loc4_ = false;
      _global.VxDebug("...........................................................................CTOR GPDB()");
      this.__gpdb = this;
      GUI.GPDB.GPDB.__paramDB = new Object();
      this.__goFnc = goFnc;
      this.__GuiBoot1 = mx.utils.Delegate.create(this,this.GuiBoot1);
      this.__GuiBoot2 = mx.utils.Delegate.create(this,this.GuiBoot2);
      this.__GuiBoot3 = mx.utils.Delegate.create(this,this.GuiBoot3);
      this.__onReadyCallbacks = {};
      this.__isActive = false;
      if(System.capabilities.os == "VxWorks")
      {
         this.__connection = new GUI.GPDB.GPDBCamera(this,mx.utils.Delegate.create(this,this.BootstrpGPDB),GUI.GPDB.GPDB.LOCALHOST);
      }
      else if(ipAddr == undefined || ipAddr == "")
      {
         this.__connection = new GUI.GPDB.GPDBLocal(this);
         this.BootstrpGPDB();
      }
      else
      {
         this.__connection = new GUI.GPDB.GPDBCamera(this,mx.utils.Delegate.create(this,this.AuthenticateConnection),ipAddr);
      }
   }
   function HandleParamChange(name, value)
   {
      _global.VxError("Error! GPDB.HandleParamChange(): Registered callback not handled for parameter \'" + name + "\'");
   }
   function AuthenticateConnection()
   {
      new GUI.OSD_Components.Authenticate(this.__connection,mx.utils.Delegate.create(this,this.BootstrpGPDB));
   }
   function BootstrpGPDB()
   {
      var _loc2_ = this;
      this.sync(this.__GuiBoot1);
   }
   function GuiBoot1()
   {
      _global.log("GuiBoot(1 of 7)..XML Server Connected");
      var _loc5_ = _root._url.substr(0,_root._url.lastIndexOf("/") + 1);
      var _loc4_ = "FactoryDefaults.xml";
      this.__gpdb.sendCmd("GET_FILE",_loc4_);
      this.__gpdb.sync(this.__GuiBoot2);
   }
   function GuiBoot2()
   {
      _global.log("GuiBoot(2).......Parameters Registered");
      this.__gpdb.getAllParams();
      this.__gpdb.sync(this.__GuiBoot3);
   }
   function GuiBoot3()
   {
      _global.log("GuiBoot(3).......Parameters Initalized");
      for(var _loc4_ in this.__gpdb.__onReadyCallbacks)
      {
         var _loc3_ = 0;
         while(_loc3_ < this.__gpdb.__onReadyCallbacks[_loc4_].length)
         {
            this.__gpdb.addCallback(_loc4_,this.__gpdb.__onReadyCallbacks[_loc4_][_loc3_]);
            _loc3_ = _loc3_ + 1;
         }
      }
      this.__gpdb.__isActive = true;
      this.__goFnc(this.__gpdb);
   }
   function sync(fnc)
   {
      var _loc2_ = "SYNC_EVENT_" + this.__syncNum++;
      this.__connection.sync(fnc,_loc2_);
      this.sendCmd("SYNC",_loc2_);
   }
   function getAllParams()
   {
      this.sendCmd("GET_PARAM","*");
   }
   function paramRegister(name, type, value)
   {
      if(this.paramExists(name))
      {
         _global.VxError("GPDB.register(): ERROR! Attempt to register an existing parameter: \'" + name + "\'");
      }
      else
      {
         var _loc4_ = new GUI.GPDB.GPdbParam(this,name,type,"");
         _loc4_.value = value;
         GUI.GPDB.GPDB.__paramDB[name] = _loc4_;
      }
   }
   function FlushPDB()
   {
      if(this.__dirty)
      {
         for(var _loc2_ in GUI.GPDB.GPDB.__paramDB)
         {
            if(GUI.GPDB.GPDB.__paramDB[_loc2_].dirty)
            {
               this.xmitParam(GUI.GPDB.GPDB.__paramDB[_loc2_]);
            }
         }
         this.__dirty = false;
      }
   }
   function AutoXmitParams(isAutoXmit)
   {
      this.__autoXmit = isAutoXmit;
   }
   function iterateOverPDB(fnc)
   {
      for(var _loc3_ in GUI.GPDB.GPDB.__paramDB)
      {
         var _loc2_ = this.getParam(_loc3_);
         if(!_loc2_.isEvent())
         {
            fnc(_loc3_,_loc2_.type,_loc2_.value);
         }
      }
   }
   function sendCmd(cmd, arg)
   {
      this.__connection.sendCmd(cmd,arg);
   }
   function paramSet(name, value)
   {
      var _loc3_ = this.getParam(name);
      if(_loc3_)
      {
         switch(typeof value)
         {
            case "string":
               _loc3_.value = value;
               break;
            case "number":
            case "boolean":
               _loc3_.value = value.toString();
               break;
            default:
               _global.VxError("GPDB.paramSet(" + name + ") Type \'" + typeof value + "\' not handled. (value: " + value + ")");
         }
         this.EnvokeGlobalCallbacks(name,value);
         if(_loc3_.dirty || _loc3_.isEvent())
         {
            this.xmitParam(_loc3_);
         }
      }
      _global.VxError("GPDB.paramSet() Error! Attempt to set an unregistered parameter, \'" + name + "\'");
      throw new Error("GPDB.paramSet() Error! Attempt to set an unregistered parameter, \'" + name + "\'");
   }
   function paramGet(name)
   {
      var _loc3_ = undefined;
      var _loc4_ = this.getParam(name);
      if(_loc4_)
      {
         _loc3_ = _loc4_.value;
      }
      else
      {
         _global.VxError("GPDB.paramGet() ERROR! Parameter \'" + name + "\' was not found in GPDB");
      }
      return _loc3_;
   }
   function paramGetBoolean(name)
   {
      return "true" == this.paramGet(name);
   }
   function paramGetNumber(name)
   {
      return Number(this.paramGet(name));
   }
   function paramType(name)
   {
      var _loc4_ = undefined;
      var _loc3_ = this.getParam(name);
      if(_loc3_)
      {
         _loc4_ = _loc3_.type;
      }
      else
      {
         _global.VxError("GPDB.paramType() ERROR! Parameter \'" + name + "\' was not found in GPDB");
      }
      return _loc4_;
   }
   function paramSetLocal(name, value)
   {
      var _loc4_ = this.getParam(name);
      if(_loc4_)
      {
         _loc4_.value = value;
         this.EnvokeGlobalCallbacks(name,value);
      }
      else
      {
         _global.VxError("GPDB.paramSetLocal() Error! Attempt to set an unregistered parameter, \'" + name + "\'");
      }
   }
   function paramSend(name, value)
   {
      var _loc3_ = this.getParam(name);
      if(_loc3_)
      {
         _loc3_.value = value;
         var _loc5_ = !_loc3_.isEvent() ? "" : "[EVENT]";
         if(_loc3_.dirty || _loc3_.isEvent())
         {
            this.xmitParam(_loc3_);
         }
      }
      else
      {
         _global.VxError("GPDB.paramSend() Error! Attempt to send an unregistered parameter, \'" + name + "\'");
      }
   }
   function paramRequest(name)
   {
      this.sendCmd("GET_PARAM",name);
   }
   function xmitNamedParam(name)
   {
      var _loc2_ = this.getParam(name);
      this.xmitParam(_loc2_);
   }
   function xmitParam(param)
   {
      if(this.__isActive && param)
      {
         _global.VxDebug("<---- GPDB.xmitParam(" + param.name + ", \'" + param.value + "\')");
         this.__connection.sendParam(param);
         param.dirty = false;
      }
   }
   function paramExists(name)
   {
      return GUI.GPDB.GPDB.__paramDB[name] != null ? true : false;
   }
   function getParam(name)
   {
      var _loc3_ = GUI.GPDB.GPDB.__paramDB[name];
      if(!_loc3_)
      {
         _global.VxError("GPDB.getParam: Attempt to access an non-existant parameter \'" + name + "\'");
         throw new Error("GPDB.getParam(" + name + "): Attempt to access an non-existant parameter!");
      }
      return _loc3_;
   }
   function addGlobalCallback(fnc)
   {
      if(this.__globalCallbacklist == null)
      {
         this.__globalCallbacklist = new Array();
      }
      this.__globalCallbacklist.push(fnc);
   }
   function EnvokeGlobalCallbacks(name, value)
   {
      if(this.__isActive && this.__callbacksEnabled)
      {
         for(var _loc5_ in this.__globalCallbacklist)
         {
            _global.VxLog("GPDB::EnvokeGlobalCallbacks(" + name + ", " + value + ")");
            this.__globalCallbacklist[_loc5_](name,value);
         }
      }
   }
   function addCallback(name, fnc)
   {
      var _loc2_ = this.getParam(name);
      _loc2_.addCallback(fnc);
   }
   function addCallbackWhenReady(name, fnc)
   {
      if(!this.__onReadyCallbacks[name])
      {
         this.__onReadyCallbacks[name] = [];
      }
      this.__onReadyCallbacks[name].push(fnc);
   }
   function addFlag(name, flag)
   {
      var _loc2_ = this.getParam(name);
      _loc2_.addFlag(flag);
   }
   function get callbacksEnabled()
   {
      return this.__callbacksEnabled;
   }
   function set callbacksEnabled(callbacksEnabled)
   {
      this.__callbacksEnabled = callbacksEnabled;
   }
   function dump()
   {
      for(var _loc7_ in GUI.GPDB.GPDB.__paramDB)
      {
         var _loc2_ = GUI.GPDB.GPDB.__paramDB[_loc7_].name;
         var _loc6_ = GUI.GPDB.GPDB.__paramDB[_loc7_].type;
         var _loc3_ = GUI.GPDB.GPDB.__paramDB[_loc7_].value;
         var _loc5_ = GUI.GPDB.GPDB.__paramDB[_loc7_].NumberOfCallbacks();
         var _loc4_ = _loc5_ <= 0 ? "" : "Registered Callbacks: " + _loc5_;
         _global.VxLog("GPDB.dump() " + _loc2_ + " = (" + _loc6_ + ")" + _loc3_ + _loc4_);
      }
   }
   function ShowCallbacks()
   {
      _global.VxLog("GPDB.ShowCallbacks() Registered Callbacks:");
      for(var _loc7_ in GUI.GPDB.GPDB.__paramDB)
      {
         var _loc3_ = GUI.GPDB.GPDB.__paramDB[_loc7_].name;
         var _loc6_ = GUI.GPDB.GPDB.__paramDB[_loc7_].type;
         var _loc4_ = GUI.GPDB.GPDB.__paramDB[_loc7_].value;
         var _loc2_ = GUI.GPDB.GPDB.__paramDB[_loc7_].NumberOfCallbacks();
         if(_loc2_ > 0)
         {
            var _loc5_ = _loc2_ <= 0 ? "" : " Callbacks: " + _loc2_;
         }
         _global.VxLog("      > " + _loc3_ + " = (" + _loc6_ + ")" + _loc4_ + _loc5_);
      }
   }
}
