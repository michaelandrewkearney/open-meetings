  /**
   * converts date string in the format 'yyyy-mm-dd' to a Date object
   *
   * @param date
   * @returns
   */
  export const toDateObj = (date: string): Date | null => {
    if (date === "") return null
    const year: number = parseInt(date.substring(0, 4));
    const month: number = parseInt(date.substring(5, 7)) - 1;
    const day: number = parseInt(date.slice(8));
    return new Date(year, month, day, 23, 59);
  };

   /**
   * converts Date object to the string in the format 'yyyy-mm-dd'
   *
   * @param date
   * @returns
   */
  export const toDateStr = (date: Date | null): string => {
    if (date === null) {
      return ""
    }
    const year: string = date.getFullYear().toString();
    const month: string = (date.getMonth() + 1).toString().padStart(2, "0")
    const day: string = date.getDate().toString().padStart(2, "0")

    return `${year}-${month}-${day}`
  }
  
