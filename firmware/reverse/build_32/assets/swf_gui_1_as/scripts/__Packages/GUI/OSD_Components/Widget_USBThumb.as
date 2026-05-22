class GUI.OSD_Components.Widget_USBThumb extends MovieClip
{
   var __gpdb;
   var __usbThumbPresent;
   function Widget_USBThumb()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__usbThumbPresent = this.__gpdb.paramGet("SYSTEM.DEV.USB_THUMB_DRIVE.ROOT_PATH").length > 0;
      this.addCallbacks();
      this._visible = this.__usbThumbPresent;
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("SYSTEM.DEV.USB_THUMB_DRIVE.ROOT_PATH",_loc2_);
   }
   function update(name, value)
   {
      var _loc0_ = null;
      if((_loc0_ = name) === "SYSTEM.DEV.USB_THUMB_DRIVE.ROOT_PATH")
      {
         this.__usbThumbPresent = value.length > 0;
         this._visible = this.__usbThumbPresent;
      }
   }
}
