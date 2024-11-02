# DOTMANAGER


link
file
dot
manager
dotlinker
dotman

## General Guidlines of Development
- Don't write anything to the system, in functions that do not make that clear.
   - E.g. `A.from_path()` should create an instance of `A` but not create or delete anything.



## Other Projects to Compare with 

https://github.com/SuperCuber/dotter
https://github.com/jbernard/dotfiles


## Features

### Status

I want to be able to 

### Linking

I want to have a source file or folder somewhere: `s`.
And a target folder I want to put it in, usually a version controlled directory: `t`.
The folder should move the source to the target.
Create a symlink where the source was, pointing to the target.
This should be recorded in a file in the target directory.

**Possible errors**:
- The source object do not exist.
- The target is already occupied.
- Some permission thing with moving.


```bash
# Add features
## Basic use
dotman add ~/.config/nvim ~/.dotfiles/projects/nvim # Better option as more similar to cp and mv commands
dotman add -s ~/.config/nvim -t ~/.dotfiles/projects/nvim
## Full Example
dotman add link_source target/path --target-name myfile --prefix /prefix/part --prefix-name my-prefix --prefix-description "this is not the best thing ever..."
```



## Files

### Structure
```
.dotman
- .gitignore
- config.json
- private.json
```

### Config

The idea with the file storing the linking information is that one should be able to clone the 
version controlled repository and with the `dotman` CLI-tool, be able to recreate the setup 
on a different machine.

## Status

- Project Status
- Link Status
- Config File Status


### Link Status
Unable to localize link...

In the correct case we have:
- A record in the public config about it.
- A valid preix
- A source object
- A link somewhere in the system

The Link Record can
- Not exist

The prefix
o Be home or root
- Not be home, root, nor custom
- Custom with faulty fields
   - name
   - description
- Not exist in private config
o Be valid

The Source can:
- Not exist according to the target name

The link (as given by the config) can
- Not Exist
- Exist but not be a link
- Point To the wrong thing - (not the target name from the config)
o Exist, be a link, and point to target name 

### Config Status
Are the config files valid.
Just from a strucured perspective.
Perhaps also if all link prefixes are valid.


### Project Status
One Project have multiple Links.
The links can be validated, or found the status of.
Are the config files valid.



## Variables

- ProjectStructure
- PrefixType
- CustomPrefix
- PrivateConfigFile
- PublicCustomPrefix
- Link
- PublicLink
- PublicConfigFile
- ProjectConfig
- DotProject













