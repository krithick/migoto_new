import { NavBar } from "./NavBar";

export const NavBarMatchRoute = (path) => {

    // Sort routes by length (longest first) to match more specific routes first
    const sortedRoutes = Object.keys(NavBar).sort((a, b) => b.length - a.length);

    for (const route of sortedRoutes) {
      // Escape special regex characters except for our parameter patterns
      const escapedRoute = route.replace(/[.*+?^${}()|[]\]/g, '\$&');

      // Replace parameter patterns with regex groups
      // This handles :id, :userId, :courseId, etc.
      const regexPattern = escapedRoute.replace(/\:[\w]+/g, '([^/]+)');

      // Create regex with start and end anchors
      const regex = new RegExp(`^${regexPattern}$`);

      if (regex.test(path)) {
        const result = NavBar[route];
        // Handle redirect cases (when value is a string instead of array)
        if (typeof result === 'string') {
          return NavBarMatchRoute(result); // Recursive call for redirects
        }
        return result;
      }
    }
    return ['Dashboard']; // Default fallback
  };