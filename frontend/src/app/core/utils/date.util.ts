export class DateUtil {
  static formatDate(date: string | Date): string {
    const d = new Date(date);
    return d.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  static formatDateShort(date: string | Date): string {
    const d = new Date(date);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = d.getDate();
    const month = months[d.getMonth()];
    const year = d.getFullYear();
    return `${day} ${month} ${year}`;
  }

  static formatDateTime(date: string | Date): string {
    const d = new Date(date);
    return d.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  static getRelativeTime(date: string | Date): string {
    const d = new Date(date);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} minute${diffMins > 1 ? 's' : ''}`;
    if (diffHours < 24) return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`;
    if (diffDays === 1) return 'Hier';
    if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`;
    
    return this.formatDate(d);
  }

  static isToday(date: string | Date): boolean {
    const d = new Date(date);
    const today = new Date();
    return d.toDateString() === today.toDateString();
  }

  static isYesterday(date: string | Date): boolean {
    const d = new Date(date);
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return d.toDateString() === yesterday.toDateString();
  }

  static formatActivityDateTime(date: string | Date): string {
    const d = new Date(date);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    const hours = d.getHours();
    const minutes = d.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    
    const dayName = days[d.getDay()];
    const day = d.getDate();
    const month = months[d.getMonth()];
    const year = d.getFullYear();
    
    return `${displayHours}.${displayMinutes} ${ampm}, ${dayName} ${day} ${month} ${year}`;
  }

  static formatScheduleTime(date: string | Date): string {
    const d = new Date(date);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const scheduleDate = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    
    const hours = d.getHours();
    const minutes = d.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    
    if (scheduleDate.getTime() === today.getTime()) {
      return `Today - ${displayHours}.${displayMinutes} ${ampm}`;
    }
    
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (scheduleDate.getTime() === tomorrow.getTime()) {
      return `Tomorrow - ${displayHours}.${displayMinutes} ${ampm}`;
    }
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const dayName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()];
    const day = d.getDate();
    const month = months[d.getMonth()];
    
    return `${dayName} ${day} ${month} - ${displayHours}.${displayMinutes} ${ampm}`;
  }
}

