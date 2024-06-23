import { Stack } from "expo-router";
import { useFonts } from "expo-font";

export const unstable_settings = {
  initialRouteName: "HomeScreen",
};

const Layout = () => {
  const [fontsLoaded] = useFonts({
    DMBold: require("../assets/fonts/DMSans-Bold.ttf"),
    DMMedium: require("../assets/fonts/DMSans-Medium.ttf"),
    DMRegular: require("../assets/fonts/DMSans-Regular.ttf"),
  });

  if (!fontsLoaded) {
    return null;
  }

  return (
    <Stack>
      <Stack.Screen name="HomeScreen" />
      <Stack.Screen name="MedicationScreen" />
      <Stack.Screen name="MoodTrackerScreen" />
    </Stack>
  )
};

export default Layout;

