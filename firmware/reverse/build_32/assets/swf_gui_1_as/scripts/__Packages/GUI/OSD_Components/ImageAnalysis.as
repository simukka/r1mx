class GUI.OSD_Components.ImageAnalysis extends GUI.OSD_Components.Gadget
{
   var __gpdb;
   var __focusAssist;
   var mcFocusAssist;
   var __spotMeter;
   var mcSpotMeter;
   var __currentIaEngine;
   var __currentSubEngine;
   var __currentSubEngineActive;
   static var __manager;
   var __show = false;
   function ImageAnalysis()
   {
      super();
      GUI.OSD_Components.ImageAnalysis.__manager = this;
      this.__gpdb = _global.gpdb;
      this.attachMovie("FocusAssistMC","mcFocusAssist",this.getNextHighestDepth(),{_x:0,_y:424});
      this.__focusAssist = this.mcFocusAssist;
      this.attachMovie("SpotMeterDisplayMC","mcSpotMeter",this.getNextHighestDepth(),{_x:0,_y:0});
      this.__spotMeter = this.mcSpotMeter;
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.ImageAnalysis.__manager === undefined)
      {
         _global.VxError("ImageAnalysis::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.ImageAnalysis.__manager;
   }
   function Activate(activate)
   {
      _global.VxDebug("ImageAnalysis::Activate(" + activate + ") current engine: " + this.__currentIaEngine);
      var _loc6_ = "true" == this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER_ENABLED");
      var _loc5_ = this.__currentIaEngine;
      var _loc4_ = !_loc6_ ? this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.HUD_METER") : this.__gpdb.paramGet("GUI.SOFTKEY.IMAGE_ANALYSIS.ASSIST_METER");
      if(activate && _loc4_ != _loc5_)
      {
         this.ActivateSubEngine(_loc5_,false);
         this.__gpdb.paramSet("IMAGE_ANALYSIS.METER",_loc4_);
         this.__currentIaEngine = _loc4_;
      }
      this.ActivateSubEngine(this.__currentIaEngine,activate);
      this.__gpdb.paramSet("IMAGE_ANALYSIS.ENABLE",activate);
      _global.VxDebug("ImageAnalysis::SelectActiveMeter(): Activating IA (" + this.__currentIaEngine + ")");
   }
   function ActivateSubEngine(engine, active)
   {
      var _loc4_ = engine != this.__currentSubEngine || active != this.__currentSubEngineActive;
      if(_loc4_)
      {
         this.__currentSubEngine = engine;
         this.__currentSubEngineActive = active;
         switch(engine)
         {
            case "Spot Exposure":
               GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(active);
               this.__spotMeter.Activate(active);
               break;
            case "Luma Histogram":
            case "RGB Comp Histo":
            case "Mono Histogram":
            case "Raw Histogram":
            case "RGBRaw Histo":
               GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(active);
               break;
            case "Luma Waveform":
            case "RGB Histogram":
               GUI.OSD_Components.SplatManager.GetManager().ShowMeterSplat(active);
               break;
            case "Focus Assist":
            case "Focus Assist Overlay":
               this.__focusAssist.Activate(active);
         }
      }
   }
   function getTabTargets()
   {
      return [];
   }
   function onInputEvent(name, value)
   {
      var _loc4_ = true;
      var _loc5_ = this.__gpdb.paramGet("IMAGE_ANALYSIS.METER");
      switch(_loc5_)
      {
         case "Focus Assist":
         case "Focus Assist Overlay":
            _loc4_ = this.__focusAssist.onInputEvent(name,value);
            break;
         case "Spot Exposure":
            _loc4_ = this.__spotMeter.onInputEvent(name,value);
            break;
         default:
            _loc4_ = false;
      }
      return _loc4_;
   }
}
