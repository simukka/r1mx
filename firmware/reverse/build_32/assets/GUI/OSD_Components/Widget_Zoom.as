class GUI.OSD_Components.Widget_Zoom
{
   var __DSymbol;
   var __ZOOM;
   var __gpdb;
   var __percentSymbol;
   function Widget_Zoom()
   {
      this.__gpdb = _global.gpdb;
      this.SetZoom(this.__gpdb.paramGet("SYSTEM.DEV.LENS.FEEDBACK.ZOOM"),this.__gpdb.paramGetBoolean("SYSTEM.DEV.LENS.IS_PRIME"));
      this.AddCallbacks();
   }
   function SetZoom(value, isPrime)
   {
      var _loc2_;
      var _loc3_;
      if(isPrime)
      {
         this.__DSymbol.text = "PRIME";
         this.__DSymbol._visible = true;
         this.__ZOOM._visible = false;
         this.__percentSymbol._visible = false;
      }
      else
      {
         this.__ZOOM.text = value;
         this.__ZOOM._visible = true;
         this.__percentSymbol._visible = true;
         this.__DSymbol.text = "L";
         this.__DSymbol._visible = true;
         _loc2_ = this.__ZOOM.getTextFormat();
         _loc3_ = _loc2_.getTextExtent(this.__ZOOM.text).width;
         this.__percentSymbol._x = this.__ZOOM._x + _loc3_ + 3;
      }
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("SYSTEM.DEV.LENS.FEEDBACK.ZOOM",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.LENS.IS_PRIME",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.DEV.LENS.IS_PRIME":
         case "SYSTEM.DEV.LENS.FEEDBACK.ZOOM":
            this.SetZoom(this.__gpdb.paramGet("SYSTEM.DEV.LENS.FEEDBACK.ZOOM"),this.__gpdb.paramGetBoolean("SYSTEM.DEV.LENS.IS_PRIME"));
            return;
         default:
            return;
      }
   }
}
