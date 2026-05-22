class GUI.OSD_Components.Widget_Clipname extends MovieClip
{
   var __gpdb;
   var __CLIPNAME;
   function Widget_Clipname()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.SetClipname(this.__gpdb.paramGet("MEDIA.DIGMAG.CURRENT_CLIPNAME"));
      this.AddCallbacks();
      this.SmartEnable();
   }
   function SetClipname(value)
   {
      if("0" == this.__gpdb.paramGet("PROJECT.SLATE.REEL"))
      {
         var _loc4_ = this.__gpdb.paramGet("PROJECT.SLATE.CAMERA");
         var _loc2_ = (Number(this.__gpdb.paramGet("PROJECT.NUM_REELS_SHOT")) + 1).toString();
         while(_loc2_.length < 3)
         {
            _loc2_ = "0" + _loc2_;
         }
         this.__CLIPNAME.text = _loc4_ + _loc2_ + " (EMPTY)";
      }
      else
      {
         var _loc3_ = "true" == this.__gpdb.paramGet("PROJECT.SLATE.FORCE_REEL");
         var _loc6_ = Number(this.__gpdb.paramGet("PROJECT.SLATE.FORCE_REEL_NUM"));
         if(_loc3_)
         {
            this.__CLIPNAME.text = value.substr(0,9);
         }
         else
         {
            this.__CLIPNAME.text = value.substr(0,9);
         }
      }
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CURRENT_CLIPNAME",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.MEDIA_PATH",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "MEDIA.DIGMAG.CURRENT_CLIPNAME":
            this.SetClipname(value);
            break;
         case "MEDIA.DIGMAG.MEDIA_PATH":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
         case "VIDEO.PLAYBACK.STATE":
            this.SmartEnable();
      }
   }
   function SmartEnable()
   {
      var _loc4_ = "" == this.__gpdb.paramGet("MEDIA.DIGMAG.MEDIA_PATH");
      var _loc5_ = "true" == this.__gpdb.paramGet("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc3_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc2_ = !_loc4_ && !_loc5_ && !_loc3_;
      this._visible = _loc2_;
   }
}
