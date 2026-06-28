class GUI.OSD_Components.Widget_FStop
{
   var __FSTOP;
   var __gpdb;
   function Widget_FStop()
   {
      this.__gpdb = _global.gpdb;
      this.setFStop(this.__gpdb.paramGetNumber("SYSTEM.DEV.LENS.FEEDBACK.APERTURE"));
      this.addCallbacks();
   }
   function setFStop(value)
   {
      this.__FSTOP.text = _global.ShowDecimalPlaces(value,1,true);
   }
   function addCallbacks()
   {
      this.__gpdb.addCallback("SYSTEM.DEV.LENS.FEEDBACK.APERTURE",mx.utils.Delegate.create(this,this.update));
   }
   function update(name, value)
   {
      var _loc0_;
      if((_loc0_ = name) === "SYSTEM.DEV.LENS.FEEDBACK.APERTURE")
      {
         this.setFStop(this.__gpdb.paramGetNumber("SYSTEM.DEV.LENS.FEEDBACK.APERTURE"));
      }
   }
}
