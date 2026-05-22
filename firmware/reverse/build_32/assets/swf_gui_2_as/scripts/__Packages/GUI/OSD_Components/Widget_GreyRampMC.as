class GUI.OSD_Components.Widget_GreyRampMC extends MovieClip
{
   var __gpdb;
   function Widget_GreyRampMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.AddCallbacks();
      this.SmartEnable();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.OSD.SHOW.GREYRAMP_CHART",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",_loc2_);
   }
   function Update(param, value)
   {
      switch(param)
      {
         case "GUI.OSD.SHOW.GREYRAMP_CHART":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
         case "VIDEO.PLAYBACK.STATE":
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
            this.SmartEnable();
      }
   }
   function SmartEnable()
   {
      var _loc2_ = this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.GREYRAMP_CHART");
      var _loc4_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      var _loc6_ = this.__gpdb.paramGetBoolean("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc5_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc3_ = _loc2_ && !_loc6_ && !_loc5_ && !_loc4_;
      this._visible = _loc3_;
   }
}
