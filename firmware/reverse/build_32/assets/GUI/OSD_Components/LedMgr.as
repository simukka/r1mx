class GUI.OSD_Components.LedMgr
{
   var __gpdb;
   static var __manager;
   var __isBodyHot = false;
   var __isSensorHot = false;
   var __isRecording = false;
   var __isWaitingForErrACK = false;
   var __isActiveWarning = false;
   function LedMgr()
   {
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.LedMgr.__manager = this;
      this.addCallbacks();
      this.__gpdb.paramSet("SYSTEM.DEV.EVF.RAWOUTPUT.LED_1","OFF");
      this.__gpdb.paramSet("GUI.RAWOUTPUT.LED_1","OFF");
      this.__gpdb.paramSet("GUI.RAWOUTPUT.LED_2","ON");
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.LedMgr.__manager === undefined)
      {
         _global.VxError("LedMgr::GetManager(): ERROR! Called before created!");
      }
      return GUI.OSD_Components.LedMgr.__manager;
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",_loc2_);
      this.__gpdb.addCallback("SYSTEM.THERMAL.SENSOR_OVERTEMP",_loc2_);
      this.__gpdb.addCallback("SYSTEM.THERMAL.BODY_OVERTEMP",_loc2_);
      this.__gpdb.addCallback("SYSTEM.ERROR.GENERAL",_loc2_);
   }
   function update(name, value)
   {
      switch(name)
      {
         case "VIDEO.RECORD.STATE":
            this.__isRecording = value != "IDLE";
            break;
         case "SYSTEM.THERMAL.SENSOR_OVERTEMP":
            this.__isSensorHot = value == "true";
            break;
         case "SYSTEM.THERMAL.BODY_OVERTEMP":
            this.__isBodyHot = value == "true";
            break;
         case "SYSTEM.ERROR.GENERAL":
            this.__isWaitingForErrACK = value != "NONE";
      }
      this.SetLEDs();
   }
   function FlagWarning(active)
   {
      this.__isActiveWarning = active;
      this.SetLEDs();
   }
   function SetLEDs()
   {
      var _loc2_ = "OFF";
      var _loc3_ = "OFF";
      var _loc4_ = "OFF";
      if(this.__isRecording)
      {
         if(this.__gpdb.paramGet("GUI.PROGRAM.TALLY") == "TALENT")
         {
            _loc4_ = "ON";
         }
         else
         {
            _loc4_ = "OFF";
         }
         _loc2_ = "RED";
      }
      else
      {
         _loc4_ = "OFF";
         _loc2_ = "OFF";
      }
      if(this.__isBodyHot)
      {
         _loc2_ = "BLINK_RED";
         _loc3_ = "BLINK_1";
      }
      else if(this.__isSensorHot)
      {
         _loc2_ = "BLINK_AMBER";
         _loc3_ = "BLINK_1";
      }
      else
      {
         _loc3_ = "ON";
      }
      if(this.__isWaitingForErrACK || this.__isActiveWarning)
      {
         _loc2_ = "BLINK_GREEN";
         _loc3_ = "BLINK_1";
      }
      this.__gpdb.paramSet("GUI.RAWOUTPUT.LED_1",_loc2_);
      this.__gpdb.paramSet("GUI.RAWOUTPUT.LED_2",_loc3_);
      this.__gpdb.paramSet("SYSTEM.DEV.EVF.RAWOUTPUT.LED_1",_loc4_);
   }
}
