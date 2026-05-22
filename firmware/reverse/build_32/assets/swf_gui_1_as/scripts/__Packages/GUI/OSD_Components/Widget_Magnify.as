class GUI.OSD_Components.Widget_Magnify extends MovieClip
{
   var __mc;
   var __gpdb;
   var __playback = false;
   var MONITOR_WIDTH = 1280;
   var MONITOR_HEIGHT = 720;
   var SENSOR_4K_WIDTH = 2240;
   var SENSOR_4K_HEIGHT = 1260;
   var SENSOR_3K_WIDTH = 1684;
   var SENSOR_3K_HEIGHT = 945;
   var SENSOR_2K_WIDTH = 1494;
   var SENSOR_2K_HEIGHT = 840;
   var SENSOR_1080_WIDTH = 2240;
   var SENSOR_1080_HEIGHT = 1260;
   var __viewAreaWidth = GUI.OSD_Components.Widget_Magnify.prototype.MONITOR_WIDTH;
   var __viewAreaHeight = GUI.OSD_Components.Widget_Magnify.prototype.MONITOR_HEIGHT;
   var __sensorAreaWidth = GUI.OSD_Components.Widget_Magnify.prototype.SENSOR_4K_WIDTH;
   var __sensorAreaHeight = GUI.OSD_Components.Widget_Magnify.prototype.SENSOR_4K_HEIGHT;
   var __gadgetHeight = 62;
   var __dx = 0;
   var __dy = 0;
   var __viewX = 0;
   var __viewY = 0;
   function Widget_Magnify()
   {
      super();
      _global.VxDebug("...........................................................................CTOR Widget_Magnify()");
      this.__mc = this;
      this.__gpdb = _global.gpdb;
      this._visible = false;
      this.HandleZoom();
      this.AddCallbacks();
   }
   function Activate(enable)
   {
      _global.VxDebug("Widget_Magnify::Activate(" + enable + ")");
      this.HandleZoom();
      this._visible = enable;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.MAG1TO1",_loc2_);
   }
   function Update(param, value)
   {
      switch(param)
      {
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
         case "PROJECT.MODE_MATRIX.RESOLUTION":
         case "VIDEO.PLAYBACK.STATE":
         case "IMAGE_ANALYSIS.MAGNIFICATION.MAG1TO1":
            this.HandleZoom();
      }
   }
   function HandleZoom()
   {
      var _loc2_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      if(_loc2_)
      {
         this.ScaleZoomWidget();
      }
   }
   function ScaleZoomWidget()
   {
      var _loc5_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc3_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION");
      var _loc4_ = true;
      switch(_loc3_)
      {
         case "4K2:1":
         case "4K":
         case "4K1.2:1":
         case "4KHS":
         case "4KHD":
         case "4K40":
         case "4KOS":
         case "4.5K":
            this.__mc.gotoAndStop("ZOOM_4K");
            break;
         case "3K2:1":
         case "3K":
         case "3K1.2:1":
            this.__mc.gotoAndStop("ZOOM_3K");
            break;
         case "2K2:1":
         case "2K":
         case "2K1.2:1":
            this.__mc.gotoAndStop("ZOOM_2K");
            break;
         case "RGB1080P":
         case "RGB720P":
            this.__mc.gotoAndStop("ZOOM_1080");
            _loc4_ = false;
            break;
         default:
            _global.VxError("Widget_Magnify::ScaleZoomWidget() Unknown resolution, \'" + _loc3_ + "\'. Ignoring.");
      }
      this.__gpdb.paramSet("IMAGE_ANALYSIS.MAGNIFICATION.MAG1TO1",_loc4_);
      return _loc4_;
   }
}
