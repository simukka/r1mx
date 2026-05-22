class GUI.OSD_Components.Widget_EI extends MovieClip
{
   var __gpdb;
   var __ISO;
   var __dbSymbol;
   function Widget_EI(parent, xPos, yPos)
   {
      super();
      this.__gpdb = _global.gpdb;
      this.AddCallbacks();
      this.Paint(this.__gpdb.paramGet("GUI.PAINT.EXPOSURE.ISO"));
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.PAINT.EXPOSURE.ISO",_loc2_);
   }
   function Paint(asa)
   {
      this.__ISO.text = asa;
      this.__dbSymbol._visible = false;
   }
   function Update(name, value)
   {
      var _loc0_ = null;
      if((_loc0_ = name) === "GUI.PAINT.EXPOSURE.ISO")
      {
         this.Paint(value);
      }
   }
}
