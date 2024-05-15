DESCRIPTION = "Enigma2 is an experimental, but useful framebuffer-based frontend for DVB functions"
MAINTAINER = "OpenPLi team <info@openpli.org>"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b234ee4d69f5fce4486a80fdaf4a4263"

inherit gitpkgv externalsrc

S = "${FILE_DIRNAME}"
WORKDIR = "${S}/build"

PV = "develop+git"
PKGV = "develop+git${GITPKGV}"

FILES_${PN} += "${datadir}/keymaps"
FILES_${PN}-meta = "${datadir}/meta"
PACKAGES =+ "${PN}-src"
PACKAGES += "${PN}-meta"
PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit autotools pkgconfig pythonnative

do_unpack[noexec] = "1"
do_populate_sysroot[noexec] = "1"
do_populate_lic[noexec] = "1"
do_packagedata[noexec] = "1"
do_package_write_ipk[noexec] = "1"
do_rm_work[noexec] = "1"
do_rm_work_all[noexec] = "1"

ACLOCALDIR = "${B}/aclocal-copy"
e2_copy_aclocal () {
	rm -rf ${ACLOCALDIR}/
	mkdir -p ${ACLOCALDIR}/
	if [ -d ${STAGING_DATADIR_NATIVE}/aclocal ]; then
		cp-noerror ${STAGING_DATADIR_NATIVE}/aclocal/ ${ACLOCALDIR}/
	fi
	if [ -d ${STAGING_DATADIR}/aclocal -a "${STAGING_DATADIR_NATIVE}/aclocal" != "${STAGING_DATADIR}/aclocal" ]; then
		cp-noerror ${STAGING_DATADIR}/aclocal/ ${ACLOCALDIR}/
	fi
}

EXTRACONFFUNCS += "e2_copy_aclocal"

bindir = "/usr/bin"
sbindir = "/usr/sbin"

EXTRA_OECONF = "\
	--enable-maintainer-mode --with-target=native --with-libsdl=no --with-boxtype=${MACHINE} \
	--enable-dependency-tracking \
	${@bb.utils.contains("MACHINE_FEATURES", "textlcd", "--with-textlcd" , "", d)} \
	--with-boxbrand="${BOX_BRAND}" \
	--with-stbplatform=${STB_PLATFORM} \
	--with-e2rev=${SRCPV} \
	${@bb.utils.contains_any("MACHINE_FEATURES", "7segment 7seg", "--with-7segment" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "uianimation", "--with-libvugles2" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "osdanimation", "--with-osdanimation" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "hiaccel", "--with-libhiaccel" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "bwlcd128", "--with-bwlcd128" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "bwlcd140", "--with-bwlcd140" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "bwlcd255", "--with-bwlcd255" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "colorlcd220", "--with-colorlcd220" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "colorlcd390", "--with-colorlcd390" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "colorlcd400", "--with-colorlcd400" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "colorlcd480", "--with-colorlcd480" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "colorlcd720", "--with-colorlcd720" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "colorlcd800", "--with-colorlcd800" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "nolcd", "--with-nolcd" , "", d)} \
	${@bb.utils.contains("MACHINE_FEATURES", "fcc", "--with-fcc" , "", d)} \
	BUILD_SYS=${BUILD_SYS} \
	HOST_SYS=${HOST_SYS} \
	STAGING_INCDIR=${STAGING_INCDIR} \
	STAGING_LIBDIR=${STAGING_LIBDIR} \
	"

do_install_append() {
	install -d ${D}/usr/share/keymaps
}

python populate_packages_prepend () {
    enigma2_plugindir = bb.data.expand('${libdir}/enigma2/python/Plugins', d)
    do_split_packages(d, enigma2_plugindir, '(.*?/.*?)/.*', 'enigma2-plugin-%s', '%s ', recursive=True, match_path=True, prepend=True, extra_depends="enigma2")
}
