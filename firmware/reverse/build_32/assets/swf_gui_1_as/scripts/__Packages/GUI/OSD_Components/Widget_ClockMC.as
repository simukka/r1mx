class GUI.OSD_Components.Widget_ClockMC extends GUI.OSD_Components.Gizmo
{
   var __gpdb;
   function Widget_ClockMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this._visible = false;
   }
}
