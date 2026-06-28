class GUI.OSD_Components.Widget_VarispeedMC extends MovieClip
{
   var __gpdb;
   function Widget_VarispeedMC(parent, xPos, yPos)
   {
      super();
      this.__gpdb = _global.gpdb;
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "PROJECT.MODE_MATRIX.FRAME_RATE":
         case "PROJECT.MODE_MATRIX.RESOLUTION":
            this.__gpdb.paramSet("VIDEO.RECORD.VARISPEED.ENABLED",false);
            this.SetVarispeedFramerate(Number(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE")));
            return;
         default:
            _global.VxError("Widget_VarispeedMC.Update() ERROR! Unknown parameter, \'" + name + "\'. Ignoring.");
            return;
      }
   }
   function SetVarispeedFramerate(fps)
   {
      var _loc2_ = Math.round(fps);
      this.__gpdb.paramSet("GUI.RECORD.VARISPEED.FRAME_RATE",_loc2_);
      this.__gpdb.paramSet("GUI.RECORD.VARISPEED.RAMP.END_FRAME_RATE",_loc2_);
   }
}
