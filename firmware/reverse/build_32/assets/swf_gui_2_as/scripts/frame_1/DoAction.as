function Init()
{
   if(System.capabilities.os != "VxWorks")
   {
      _global.VxLogWvEvent = function(msg)
      {
      };
      _global.VxDebug = function(msg)
      {
      };
      _global.VxForceRedraw = function()
      {
      };
      _global.VxCapability = function()
      {
      };
      _global.VxLog = function()
      {
      };
   }
   var _loc2_ = new Date();
   CheckIP();
}
function ConnectGPDB()
{
   var _loc2_ = mx.utils.Delegate.create(this,CreateGPDB);
   if(System.capabilities.os != "VxWorks")
   {
      attachMovie("RemoteConnectMC","mcRemote",getNextHighestDepth(),{__goFnc:_loc2_});
   }
   else
   {
      CreateGPDB("");
   }
}
function CreateGPDB(cameraIP)
{
   var _loc2_ = osd.getGoFnc();
   try
   {
      _global.gpdb = new GUI.GPDB.GPDB(_loc2_,cameraIP);
   }
   catch(e:Error)
   {
   }
}
function CheckIP()
{
   if(System.capabilities.os != "VxWorks")
   {
      cookie = SharedObject.getLocal("Sundance","/");
      var _loc2_ = isNaN(cookie.data.socPort) || isNaN(cookie.data.socAddr1) || isNaN(cookie.data.socAddr2) || isNaN(cookie.data.socAddr3) || isNaN(cookie.data.socAddr4);
      var _loc1_ = cookie.data.socPort;
      var _loc3_ = cookie.data.socAddr1 + "." + cookie.data.socAddr2 + "." + cookie.data.socAddr3 + "." + cookie.data.socAddr4;
      if(!_loc2_)
      {
      }
   }
}
_quality = "BEST";
try
{
   Init();
   attachMovie("OSD","osd",getNextHighestDepth());
   ConnectGPDB();
}
catch(e:Error)
{
}
stop();
_global.log = function(msg)
{
   VxLog(msg);
};
Object.prototype.copy = function(deep)
{
   var _loc2_ = {};
   _loc2_.__proto__ = this.__proto__;
   for(var _loc4_ in this)
   {
      if(deep && typeof this[_loc4_] == "object")
      {
         _loc2_[_loc4_] = this[_loc4_].copy(deep);
      }
      else
      {
         _loc2_[_loc4_] = this[_loc4_];
      }
   }
   return _loc2_;
};
ASSetPropFlags(Object.prototype,["copy"],1);
Array.prototype.copy = function(deep)
{
   var _loc3_ = [];
   _loc3_.__proto__ = this.__proto__;
   var _loc2_ = 0;
   while(_loc2_ < this.length)
   {
      if(deep && typeof this[_loc2_] == "object")
      {
         _loc3_[_loc2_] = this[_loc2_].copy(deep);
      }
      else
      {
         _loc3_[_loc2_] = this[_loc2_];
      }
      _loc2_ = _loc2_ + 1;
   }
   return _loc3_;
};
ASSetPropFlags(Array.prototype,["copy"],1);
Array.prototype.search = function(ago, from, strict)
{
   if(from == undefined || from >= this.length)
   {
      from = 0;
   }
   strict = strict != undefined ? strict : false;
   var _loc2_ = from;
   while(_loc2_ < this.length)
   {
      if(this[_loc2_] == ago)
      {
         if(!strict)
         {
            return _loc2_;
         }
         if(this[_loc2_].__proto__ == ago.__proto__)
         {
            return _loc2_;
         }
      }
      _loc2_ = _loc2_ + 1;
   }
   return -1;
};
_global.ShowDecimalPlaces = function(num, decPlaces, hide00)
{
   var _loc6_ = undefined;
   var _loc7_ = num < 0;
   if(_loc7_)
   {
      num = - num;
   }
   var _loc3_ = Math.floor(num);
   var _loc8_ = num - _loc3_;
   if(_loc7_)
   {
      _loc3_ = - _loc3_;
   }
   var _loc5_ = _loc3_.toString();
   var _loc1_ = _loc8_ != 0 ? _loc8_.toString().substr(1) : ".0000000000";
   while(_loc1_.length < decPlaces)
   {
      _loc1_ += "0";
   }
   _loc1_ = decPlaces <= 0 ? "" : _loc1_.substr(0,decPlaces + 1);
   if(hide00)
   {
      _loc6_ = Number(_loc1_) != 0 ? _loc5_ + _loc1_ : _loc5_;
   }
   else
   {
      _loc6_ = _loc5_ + _loc1_;
   }
   return _loc6_;
};
