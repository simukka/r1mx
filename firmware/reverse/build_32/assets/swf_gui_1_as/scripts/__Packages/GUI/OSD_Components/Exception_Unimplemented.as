class GUI.OSD_Components.Exception_Unimplemented extends Error
{
   function Exception_Unimplemented(details)
   {
      super();
      this.message = details;
   }
}
