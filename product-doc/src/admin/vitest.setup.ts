import { setSkillMarkdownDiskLoader } from "./src/pages/tools/skillRegistryCatalog";
import { getSkillMarkdownFromDisk } from "./src/pages/tools/skillRegistryNodeFs";

setSkillMarkdownDiskLoader(getSkillMarkdownFromDisk);
