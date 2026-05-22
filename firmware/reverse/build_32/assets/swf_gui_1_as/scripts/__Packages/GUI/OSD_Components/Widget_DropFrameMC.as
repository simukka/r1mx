class GUI.OSD_Components.Widget_DropFrameMC extends MovieClip
{
   var __gpdb;
   var __statusBox;
   var mcBox;
   var __FRAME_COUNT;
   function Widget_DropFrameMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.attachMovie("StatusBoxMC","mcBox",this.getNextHighestDepth(),{_x:18,_y:58});
      this.__statusBox = this.mcBox;
      this.AddCallbacks();
      this.Paint(this.__gpdb.paramGet("VIDEO.RECORD.DROPPEDFRAMECOUNT"));
   }
   function Paint(droppedFrameCountStr)
   {
      var _loc3_ = Number(droppedFrameCountStr);
      var _loc4_ = undefined;
      if(_loc3_ == 0)
      {
         this.__FRAME_COUNT.text = "0";
         this.__statusBox.SetColor("green");
         _loc4_ = 39168;
      }
      else
      {
         if(_loc3_ > 999)
         {
            _loc3_ = 999;
         }
         this.__FRAME_COUNT.text = _loc3_.toString();
         this.__statusBox.SetColor("red");
         _loc4_ = 16711680;
      }
      var _loc2_ = this.__FRAME_COUNT.getTextFormat();
      _loc2_.align = "center";
      _loc2_.color = _loc4_;
      if(droppedFrameCountStr.length > 2)
      {
         _loc2_.size = 24;
         this.__FRAME_COUNT._y = 22;
      }
      else
      {
         _loc2_.size = 32;
         this.__FRAME_COUNT._y = 16;
      }
      this.__FRAME_COUNT.setTextFormat(_loc2_);
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("VIDEO.RECORD.DROPPEDFRAMECOUNT",_loc2_);
   }
   function update(name, value)
   {
      var _loc0_ = null;
      if((_loc0_ = name) === "VIDEO.RECORD.DROPPEDFRAMECOUNT")
      {
         this.Paint(value);
      }
   }
}
