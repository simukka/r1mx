class GUI.OSD_Components.PanelWidget extends GUI.OSD_Components.Gizmo
{
   var __panelWidgetMC;
   var __menuMgr;
   var __cbLabel;
   var __cbAction;
   var __cbData;
   var __osd;
   var __arg0;
   var __arg1;
   var __id;
   function PanelWidget()
   {
      super();
      this.__panelWidgetMC = this;
      this.__menuMgr = GUI.OSD_Components.MenuManager.GetManager();
   }
   function getWidth()
   {
      return this.__panelWidgetMC._width;
   }
   function setHandler(cbLabel, cbAction, cbData, osd)
   {
      this.__cbLabel = cbLabel;
      this.__cbAction = cbAction;
      this.__cbData = cbData;
      this.__osd = osd;
      this.__panelWidgetMC._onRelease = mx.utils.Delegate.create(this,this.handleEveryButtonRelease);
   }
   function handleEveryButtonRelease()
   {
      this.__menuMgr.HandlePanelWidgetRelease(this.__cbLabel,this.__cbAction,this.__cbData,this.__arg0,this.__arg1);
   }
   function onCommit(arg0, arg1)
   {
      this.__arg0 = arg0;
      this.__arg1 = arg1;
   }
   function id()
   {
      return this.__id;
   }
   function move(x, y)
   {
      this.__panelWidgetMC._x = x;
      this.__panelWidgetMC._y = y;
   }
}
