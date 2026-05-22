class GUI.OSD_Components.TimeManager
{
   var __gpdb;
   var __year;
   var __month;
   var __day;
   var __hour;
   var __minute;
   var __second;
   static var __manager;
   var __setSystemClock = false;
   function TimeManager()
   {
      _global.VxDebug("...........................................................................CTOR TimeManager()");
      GUI.OSD_Components.TimeManager.__manager = this;
      this.__gpdb = _global.gpdb;
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_YEAR","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_MONTH","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_DAY","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_HOUR","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_MINUTE","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_SECOND","false");
      this.InitGUITime();
      this.HandleSetTimeZone();
      this.AddCallbacks();
      this.__gpdb.paramSet("SYSTEM.TIME.REFRESH",true);
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.TimeManager.__manager === undefined)
      {
         _global.VxError("ERROR! TimeManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.TimeManager.__manager;
   }
   function AddCallbacks()
   {
      var _loc3_ = mx.utils.Delegate.create(this,this.HandleSetTimeZone);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.GMT_OFFSET",_loc3_);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_GMT_OFFSET",_loc3_);
      this.__gpdb.addCallback("SYSTEM.TIME.CURRENT",mx.utils.Delegate.create(this,this.HandleCurrentTime));
      var _loc2_ = mx.utils.Delegate.create(this,this.HandleModClockCB);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_YEAR",_loc2_);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_MONTH",_loc2_);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_DAY",_loc2_);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_HOUR",_loc2_);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_MINUTE",_loc2_);
      this.__gpdb.addCallback("GUI.SYSTEM_DATE.MODIFY_SECOND",_loc2_);
   }
   function HandleSetTimeZone(param, value)
   {
      if(this.__gpdb.paramGetBoolean("GUI.SYSTEM_DATE.MODIFY_GMT_OFFSET"))
      {
         var _loc3_ = Number(this.__gpdb.paramGet("GUI.SYSTEM_DATE.GMT_OFFSET"));
         var _loc2_ = _loc3_ * 60;
         this.__gpdb.paramSet("SYSTEM.TIME.GMTOFFSET_MINUTES",_loc2_);
      }
      else
      {
         this.__gpdb.paramSet("SYSTEM.TIME.GMTOFFSET_MINUTES",0);
      }
   }
   function HandleCurrentTime(param, value)
   {
      if(this.__setSystemClock)
      {
         _global.VxLog("TimeManager::HandleCurrentTime() Setting System Clock: " + this.__year + this.__month + this.__day + "_" + this.__hour + ":" + this.__minute + ":" + this.__second);
         this.SetSystemClock();
      }
      else
      {
         this.__year = value.substr(0,4);
         this.__month = value.substr(4,2);
         this.__day = value.substr(6,2);
         this.__hour = value.substr(9,2);
         this.__minute = value.substr(12,2);
         this.__second = value.substr(15,2);
         this.__gpdb.paramSet("GUI.SYSTEM_DATE.YEAR",this.__year);
         this.__gpdb.paramSet("GUI.SYSTEM_DATE.MONTH",this.__month);
         this.__gpdb.paramSet("GUI.SYSTEM_DATE.DAY",this.__day);
         this.__gpdb.paramSet("GUI.SYSTEM_DATE.HOUR",this.__hour);
         this.__gpdb.paramSet("GUI.SYSTEM_DATE.MINUTE",this.__minute);
         this.__gpdb.paramSet("GUI.SYSTEM_DATE.SECOND",this.__second);
      }
   }
   function InitGUITime()
   {
      var _loc2_ = this.__gpdb.paramGet("SYSTEM.TIME.CURRENT");
      this.__year = _loc2_.substr(0,4);
      this.__month = _loc2_.substr(4,2);
      this.__day = _loc2_.substr(6,2);
      this.__hour = _loc2_.substr(9,2);
      this.__minute = _loc2_.substr(12,2);
      this.__second = _loc2_.substr(15,2);
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.YEAR",this.__year);
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MONTH",this.__month);
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.DAY",this.__day);
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.HOUR",this.__hour);
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MINUTE",this.__minute);
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.SECOND",this.__second);
   }
   function HandleModClockCB(param, value)
   {
   }
   function HandleSetClock()
   {
      this.__setSystemClock = true;
      this.__gpdb.paramSet("SYSTEM.TIME.REFRESH",true);
   }
   function SetSystemClock()
   {
      this.__setSystemClock = false;
      var _loc9_ = "true" == this.__gpdb.paramGet("GUI.SYSTEM_DATE.MODIFY_YEAR");
      var _loc13_ = "true" == this.__gpdb.paramGet("GUI.SYSTEM_DATE.MODIFY_MONTH");
      var _loc11_ = "true" == this.__gpdb.paramGet("GUI.SYSTEM_DATE.MODIFY_DAY");
      var _loc12_ = "true" == this.__gpdb.paramGet("GUI.SYSTEM_DATE.MODIFY_HOUR");
      var _loc10_ = "true" == this.__gpdb.paramGet("GUI.SYSTEM_DATE.MODIFY_MINUTE");
      var _loc14_ = "true" == this.__gpdb.paramGet("GUI.SYSTEM_DATE.MODIFY_SECOND");
      var _loc15_ = !_loc9_ ? "----" : this.__gpdb.paramGet("GUI.SYSTEM_DATE.YEAR");
      var _loc4_ = !_loc13_ ? "--" : this.__gpdb.paramGet("GUI.SYSTEM_DATE.MONTH");
      if(_loc4_.length == 1)
      {
         _loc4_ = "0" + _loc4_;
      }
      var _loc3_ = !_loc11_ ? "--" : this.__gpdb.paramGet("GUI.SYSTEM_DATE.DAY");
      if(_loc3_.length == 1)
      {
         _loc3_ = "0" + _loc3_;
      }
      var _loc7_ = !_loc12_ ? "--" : this.__gpdb.paramGet("GUI.SYSTEM_DATE.HOUR");
      if(_loc7_.length == 1)
      {
         _loc7_ = "0" + _loc7_;
      }
      var _loc5_ = !_loc10_ ? "--" : this.__gpdb.paramGet("GUI.SYSTEM_DATE.MINUTE");
      if(_loc5_.length == 1)
      {
         _loc5_ = "0" + _loc5_;
      }
      var _loc6_ = !_loc14_ ? "--" : this.__gpdb.paramGet("GUI.SYSTEM_DATE.SECOND");
      if(_loc6_.length == 1)
      {
         _loc6_ = "0" + _loc6_;
      }
      var _loc8_ = _loc15_ + _loc4_ + _loc3_ + "_" + _loc7_ + ":" + _loc5_ + ":" + _loc6_;
      if(_loc9_ || _loc13_ || _loc11_ || _loc12_ || _loc10_ || _loc14_)
      {
         this.__gpdb.paramSet("SYSTEM.TIME.SET",_loc8_);
         _global.VxLog("MenuManager::HandleSetTime() newDate: " + _loc8_);
      }
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_YEAR","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_MONTH","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_DAY","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_HOUR","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_MINUTE","false");
      this.__gpdb.paramSet("GUI.SYSTEM_DATE.MODIFY_SECOND","false");
   }
}
