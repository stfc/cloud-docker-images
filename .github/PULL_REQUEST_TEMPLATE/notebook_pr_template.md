### Description:

<!--
This should be a brief one or two line description of the PR. Details should be contained in commit messages.
-->

---

### Submitter:

Have you done the following?:

* [ ] Added a new directory in the project root with a `Dockerfile` inside?
* [ ] Tested the image works?

---

### Reviewer:

Have you done the following?:

* [ ] Does the `Dockerfile` install only the necessary packages?
* [ ] Are the permissions of downloaded files onto the container are appropriate?
* [ ] Does the Dockerfile switch to `NB_UID` at the end of the file? (i.e the image is run as user, not root)
* [ ] Has the image been built successfully and pushed to Harbor?
