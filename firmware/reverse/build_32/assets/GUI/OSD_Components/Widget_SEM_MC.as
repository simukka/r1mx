class GUI.OSD_Components.Widget_SEM_MC
{
   var __B_OVER;
   var __G_OVER;
   var __R_OVER;
   var __gpdb;
   function Widget_SEM_MC()
   {
      this.__gpdb = _global.gpdb;
      this.ProcessChannelWarnings(this.__gpdb.paramGet("IMAGE_ANALYSIS.EXPOSURE.CHANNEL_WARNINGS"));
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.EXPOSURE.CHANNEL_WARNINGS",_loc2_);
   }
   function Update(name, value)
   {
      var _loc4_;
      gotoAndStop("FRAME_OVERUNDER");
      var _loc0_;
      if((_loc0_ = name) === "IMAGE_ANALYSIS.EXPOSURE.CHANNEL_WARNINGS")
      {
         this.ProcessChannelWarnings(value);
      }
   }
   function ProcessChannelWarnings(countString)
   {
      var _loc2_ = countString.split(",");
      var _loc4_ = Number(_loc2_[3]) == 1;
      var _loc5_ = Number(_loc2_[4]) == 1;
      var _loc3_ = Number(_loc2_[5]) == 1;
      this.Render(_loc4_,_loc5_,_loc3_);
   }
   function Render(rOver, gOver, bOver)
   {
      this.__R_OVER._visible = rOver;
      this.__G_OVER._visible = gOver;
      this.__B_OVER._visible = bOver;
   }
}
