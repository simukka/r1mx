class GUI.OSD_Components.ScrnProfileImportFailedMC extends GUI.OSD_Components.FullScreenMC
{
   var Deactivate;
   var NewButton;
   var __gpdb;
   var _visible;
   function ScrnProfileImportFailedMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScrnProfileImportFailedMC()");
      this.__gpdb = _global.gpdb;
      this._visible = false;
      this.NewButton("OK",mx.utils.Delegate.create(this,this.OK_FNC),0,600);
   }
   function OK_FNC()
   {
      this.Deactivate(true);
   }
   function Activate(profile)
   {
      super.Activate();
   }
}
