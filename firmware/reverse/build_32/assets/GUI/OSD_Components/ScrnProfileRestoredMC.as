class GUI.OSD_Components.ScrnProfileRestoredMC extends GUI.OSD_Components.FullScreenMC
{
   var Deactivate;
   var MESSAGE;
   var NewButton;
   var __gpdb;
   var _visible;
   var btnOK;
   function ScrnProfileRestoredMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScrnProfileRestoredMC()");
      this.__gpdb = _global.gpdb;
      this._visible = false;
      this.btnOK = this.NewButton("OK",mx.utils.Delegate.create(this,this.OK_FNC),0,600);
   }
   function OK_FNC()
   {
      this.__gpdb.paramSet("SYSTEM.PROFILE.RESTORE.REQUESTED",false);
      this.Deactivate(true);
   }
   function Activate(profile, btnVisible)
   {
      this.MESSAGE.text = "\'" + profile + "\' settings restored to Factory Default Values";
      super.Activate();
      if(btnVisible)
      {
         this.btnOK.notVisible();
      }
   }
}
