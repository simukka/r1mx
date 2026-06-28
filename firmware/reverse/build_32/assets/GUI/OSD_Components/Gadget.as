class GUI.OSD_Components.Gadget extends GUI.OSD_Components.Gizmo
{
   var __tabInfo;
   var __rows = 0;
   var GMODE_HIDE = "HIDE";
   var GMODE_CONFIG = "CONFIG";
   var GMODE_RUN = "RUN";
   var __state = GUI.OSD_Components.Gadget.prototype.GMODE_HIDE;
   function Gadget()
   {
      super();
      this.__tabInfo = new Object();
   }
   function IsEmptyGizmoGrid()
   {
      var _loc2_ = true;
      if(this.__rows != 0)
      {
         if(this.__tabInfo.targetGrid.length > 0)
         {
            _loc2_ = false;
         }
      }
      return _loc2_;
   }
   function AddTabTarget(gizmo)
   {
      if(this.__rows == 0)
      {
         this.__tabInfo.targetGrid = new Array();
         this.NewRowOfGizmos();
      }
      this.__tabInfo.targetGrid[this.__rows - 1].push(gizmo);
   }
   function NewRowOfGizmos()
   {
      this.__tabInfo.targetGrid[this.__rows] = new Array();
      this.__rows = this.__rows + 1;
   }
   function CurrentRowOfGizmos()
   {
      return this.__tabInfo.targetGrid[this.__rows - 1];
   }
   function ActivateGizmoGrid()
   {
      GUI.OSD_Components.TabManager.GetManager().push(this.__tabInfo.targetGrid);
   }
   function SetDefaultFocus(row, ndx)
   {
      this.__tabInfo.defaultFocusY = row;
      this.__tabInfo.defaultFocusX = ndx;
   }
   function onInputEvent(name, value)
   {
      throw new Error("Gadget::onInputEvent() each subclass must override this method!");
   }
   function onRequest(request, arg)
   {
   }
   function getTabTargets()
   {
      return this.__tabInfo;
   }
   function Activate(enable)
   {
      throw new Error("Gadget::Activate() MUST be handled by subclass!");
   }
}
