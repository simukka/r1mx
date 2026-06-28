class GUI.OSD_Components.ScrnProfileExportedMC extends GUI.OSD_Components.FullScreenMC
{
   var Deactivate;
   var MESSAGE;
   var NewButton;
   var __gpdb;
   var _visible;
   function ScrnProfileExportedMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScrnProfileExportedMC()");
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
      this.MESSAGE.text = profile;
      super.Activate();
   }
}
