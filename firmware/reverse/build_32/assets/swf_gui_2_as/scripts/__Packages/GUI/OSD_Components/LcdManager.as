class GUI.OSD_Components.LcdManager
{
   var __gpdb;
   static var __manager;
   var __lcdBrightness = 80;
   function LcdManager()
   {
      _global.VxDebug("...........................................................................CTOR LcdManager()");
      this.__gpdb = _global.gpdb;
      this.AddGpdbCallbacks();
      this.__lcdBrightness = Number(this.__gpdb.paramGet("SYSTEM.DEV.LCD.BRIGHTNESS"));
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.LcdManager.__manager === undefined)
      {
         _global.VxError("ERROR! LcdManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.LcdManager.__manager;
   }
   function AddGpdbCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.HandleLcdKey);
      this.__gpdb.addCallback("SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW2",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW3",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4_LONG",_loc2_);
   }
   function HandleLcdKey(param, value)
   {
      var _loc2_ = undefined;
      if(value == "true")
      {
         switch(param)
         {
            case "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW1":
               _loc2_ = "true" == this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED");
               this.__gpdb.paramSet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED",(!_loc2_).toString());
               break;
            case "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW2":
               this.__lcdBrightness += 10;
               if(this.__lcdBrightness > 100)
               {
                  this.__lcdBrightness = 100;
               }
               this.__gpdb.paramSet("SYSTEM.DEV.LCD.BRIGHTNESS",this.__lcdBrightness.toString());
               if(this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.GREYRAMP_CHART") == false)
               {
                  this.__gpdb.paramSet("GUI.OSD.SHOW.GREYRAMP_CHART",true);
                  this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_3_INITIALIZE_GUI_STATE");
                  this.__gpdb.paramSet("GUI.OSD.SHOW.GREYRAMP_CHART",false);
               }
               break;
            case "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW3":
               this.__lcdBrightness -= 10;
               if(this.__lcdBrightness < 10)
               {
                  this.__lcdBrightness = 10;
               }
               this.__gpdb.paramSet("SYSTEM.DEV.LCD.BRIGHTNESS",this.__lcdBrightness.toString());
               if(this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.GREYRAMP_CHART") == false)
               {
                  this.__gpdb.paramSet("GUI.OSD.SHOW.GREYRAMP_CHART",true);
                  this.__gpdb.paramSet("GUI.RUN_STATE","GUI_STATE_3_INITIALIZE_GUI_STATE");
                  this.__gpdb.paramSet("GUI.OSD.SHOW.GREYRAMP_CHART",false);
               }
               break;
            case "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4":
               if("true" == this.__gpdb.paramGet("SYSTEM.DEV.LCD.ENABLED"))
               {
                  if("false" == this.__gpdb.paramGet("SYSTEM.DEV.LCD.ENABLE54SCALING"))
                  {
                     this.__gpdb.paramSet("SYSTEM.DEV.LCD.ENABLE54SCALING","true");
                  }
                  else
                  {
                     this.__gpdb.paramSet("SYSTEM.DEV.LCD.ENABLE54SCALING","false");
                  }
               }
               break;
            case "SYSTEM.DEV.LCD.RAWINPUT.BUTTON.SW4_LONG":
               break;
            default:
               throw new Error("ERROR! ButtonManager.HandleLcdKey(): Unhandled key \'" + param + "\'");
         }
      }
   }
}
