class GUI.OSD_Components.ScrnGenlockFailedMC extends GUI.OSD_Components.FullScreenMC
{
   var __gpdb;
   var ERR_MSG_1;
   var ERR_MSG_2;
   function ScrnGenlockFailedMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScrnGenlockFailedMC()");
      this.__gpdb = _global.gpdb;
      this._visible = false;
      this.NewButton("OK",mx.utils.Delegate.create(this,this.OK_FNC),0,600);
   }
   function SetMsg(line1, line2)
   {
      this.ERR_MSG_1.text = line1;
      this.ERR_MSG_2.text = line2;
   }
   function OK_FNC()
   {
      this.Deactivate(true);
   }
}
