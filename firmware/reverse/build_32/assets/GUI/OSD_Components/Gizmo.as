class GUI.OSD_Components.Gizmo extends MovieClip
{
   function Gizmo()
   {
      super();
   }
   function killFocus()
   {
   }
   function onInputEvent(name, value)
   {
      throw new Error("Gizmo::onInputEvent(\'" + name + "\', \'" + value + "\') MUST be handled by subclass!");
   }
   function focus()
   {
      throw new Error("Gizmo::focus() MUST be handled by subclass!");
   }
}
