class GUI.OSD_Components.Widget_TimelapseMC extends MovieClip
{
   var __gpdb;
   var __BURST_SIZE;
   var __INTERVAL;
   function Widget_TimelapseMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.ConfigPanel();
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("VIDEO.RECORD.TIMELAPSE.BURST_SIZE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.TIMELAPSE.INTERVAL",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.TRIGGER_MODE",_loc2_);
   }
   function ConfigPanel()
   {
      var _loc3_ = undefined;
      var _loc4_ = this.__gpdb.paramGet("GUI.RECORD.TIMELAPSE.TRIGGER_MODE");
      switch(_loc4_)
      {
         case "INTERVAL":
            _loc3_ = this.__gpdb.paramGet("VIDEO.RECORD.TIMELAPSE.INTERVAL") + " sec";
            break;
         case "ONE-SHOT":
            _loc3_ = "BURST";
            break;
         default:
            _global.VxError("Widget_TimelapseMC::ConfigPanel() Unknown trigger mode: " + _loc4_);
      }
      this.__BURST_SIZE.text = this.__gpdb.paramGet("VIDEO.RECORD.TIMELAPSE.BURST_SIZE") + " frames";
      this.__INTERVAL.text = _loc3_;
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "VIDEO.RECORD.TIMELAPSE.BURST_SIZE":
         case "VIDEO.RECORD.TIMELAPSE.INTERVAL":
         case "GUI.RECORD.TIMELAPSE.TRIGGER_MODE":
            this.ConfigPanel();
      }
   }
}
