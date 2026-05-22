class GUI.OSD_Components.ScrnProfileImportedMC extends GUI.OSD_Components.FullScreenMC
{
   var __gpdb;
   var MESSAGE;
   function ScrnProfileImportedMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScrnProfileImportedMC()");
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
      this.MESSAGE.text = "Updated camera \'look\' settings.";
      super.Activate();
   }
}
