#ifndef __lib_service_listboxservice_h
#define __lib_service_listboxservice_h

#include <lib/gdi/gpixmap.h>
#include <lib/gui/elistbox.h>
#include <lib/service/iservice.h>
#include <lib/python/python.h>
#include <set>
#include <lib/nav/core.h>

class eListboxServiceContent: public virtual iListboxContent
{
	DECLARE_REF(eListboxServiceContent);
	static ePyObject m_GetPiconNameFunc;
public:
	eListboxServiceContent();

	void addService(const eServiceReference &ref, bool beforeCurrent=false);
	void removeCurrent();
	void FillFinished();

	void setIgnoreService( const eServiceReference &service );
	void setRoot(const eServiceReference &ref, bool justSet=false);
	void getCurrent(eServiceReference &ref);

	void getPrev(eServiceReference &ref);
	void getNext(eServiceReference &ref);
	PyObject *getList();

	int getNextBeginningWithChar(char c);
	int getPrevMarkerPos();
	int getNextMarkerPos();

		/* support for marked services */
	void initMarked();
	void addMarked(const eServiceReference &ref);
	void removeMarked(const eServiceReference &ref);
	int isMarked(const eServiceReference &ref);

		/* this is NOT thread safe! */
	void markedQueryStart();
	int markedQueryNext(eServiceReference &ref);

	int lookupService(const eServiceReference &ref);
	bool setCurrent(const eServiceReference &ref);

	enum {
		visModeSimple,
		visModeComplex
	};

	void setVisualMode(int mode);

		/* only in complex mode: */
	enum {
		celServiceNumber,
		celMarkerPixmap,
		celFolderPixmap,
		celPiconPixmap,
		celRecordServicePixmap,
		celServiceEventProgressbar,
		celServiceName,
		celServiceTime,
		celServiceInfo, // "now" event
		celNextEventInfo,
		celServiceTypePixmap,
		celElements
	};

	enum {
		picDVB_S,
		picDVB_T,
		picDVB_C,
		picStream,
		picServiceGroup,
		picFolder,
		picMarker,
		picPicon,
		picRecordService,
		picServiceEventProgressbar,
		picCrypto,
		picRecord,
		picElements
	};

	void setElementPosition(int element, eRect where);
	void setElementFont(int element, gFont *font);
	void setPixmap(int type, ePtr<gPixmap> &pic);

	void sort();

	int setCurrentMarked(bool);

	int getItemHeight() { return m_itemheight; }
	void setItemHeight(int height);
	void setHideNumberMarker(bool doHide) { m_hide_number_marker = doHide; }
	void setShowTwoLines(bool twoLines) { m_show_two_lines = twoLines; }
	void setProgressViewMode(int mode) { m_progress_view_mode = mode; }
	void setProgressTextWidth(int value) { m_progress_text_width = value; }
	void setServicePiconDownsize(int value) { m_service_picon_downsize = value; }
	void setServicePiconRatio(int value) { m_service_picon_ratio = value; }
	void setServiceTypeIconMode(int mode) { m_servicetype_icon_mode = mode; }
	void setCryptoIconMode(int mode) { m_crypto_icon_mode = mode; }
	void setRecordIndicatorMode(int mode) { m_record_indicator_mode = mode; }
	void setColumnWidth(int value) { m_column_width = value; }
	void setChannelNumbersVisible(bool visible) { m_chanel_number_visible = visible; }
	void setProgressbarHeight(int value) { m_progressbar_height = value; }
	void setProgressbarBorderWidth(int value) { m_progressbar_border_width = value; }
	void setNonplayableMargins(int value) { m_nonplayable_margins = value; }
	void setItemsDistances(int value) { m_items_distances = value; }

	void setProgressUnit(const std::string &string) { m_progress_unit = string; }
	void setNumberingMode(int numberingMode) { m_numbering_mode = numberingMode; }

	static void setGetPiconNameFunc(SWIG_PYOBJECT(ePyObject) func);

	enum {
		markedForeground,
		markedForegroundSelected,
		markedBackground,
		markedBackgroundSelected,
		serviceNotAvail,
		eventForeground,
		eventForegroundSelected,
		eventborderForeground,
		eventborderForegroundSelected,
		eventForegroundFallback,
		eventForegroundSelectedFallback,
		serviceItemFallback,
		serviceSelectedFallback,
		serviceEventProgressbarColor,
		serviceEventProgressbarColorSelected,
		serviceEventProgressbarBorderColor,
		serviceEventProgressbarBorderColorSelected,
		serviceRecorded,
		servicePseudoRecorded,
		serviceStreamed,
		serviceRecordingColor,
		serviceAdvertismentColor,
		serviceDescriptionColor,
		serviceDescriptionColorSelected,
		colorElements
	};

	void setColor(int color, gRGB &col);
	bool checkServiceIsRecorded(eServiceReference ref,pNavigation::RecordType type=pNavigation::isAnyRecording);
protected:
	void cursorHome();
	void cursorEnd();
	int cursorMove(int count=1);
	int cursorValid();
	int cursorSet(int n);
	int cursorResolve(int);
	int cursorGet();
	int currentCursorSelectable();

	void cursorSave();
	void cursorRestore();
	void cursorSaveLine(int n);
	int cursorRestoreLine();
	int size();

	// void setOutputDevice ? (for allocating colors, ...) .. requires some work, though
	void setSize(const eSize &size);

		/* the following functions always refer to the selected item */
	void paint(gPainter &painter, eWindowStyle &style, const ePoint &offset, int selected);

	int m_visual_mode;
		/* for complex mode */
	eRect m_element_position[celElements];
	ePtr<gFont> m_element_font[celElements];
	ePtr<gPixmap> m_pixmaps[picElements];
	gRGB m_color[colorElements];
	bool m_color_set[colorElements];
private:
	typedef std::list<eServiceReference> list;

	list m_list;
	list::iterator m_cursor, m_saved_cursor;

	int m_cursor_number, m_saved_cursor_number, m_saved_cursor_line;
	int m_size;

	eSize m_itemsize;
	ePtr<iServiceHandler> m_service_center;
	ePtr<iListableService> m_lst;

	eServiceReference m_root;

		/* support for marked services */
	std::set<eServiceReference> m_marked;
	std::set<eServiceReference>::const_iterator m_marked_iterator;

		/* support for movemode */
	bool m_current_marked;
	void swapServices(list::iterator, list::iterator);

	eServiceReference m_is_playable_ignore;

	int m_itemheight;
	bool m_hide_number_marker;
	bool m_chanel_number_visible;
	bool m_show_two_lines;
	int m_progress_view_mode;
	int m_progress_text_width;
	int m_service_picon_downsize;
	int m_service_picon_ratio;
	int m_servicetype_icon_mode;
	int m_crypto_icon_mode;
	int m_record_indicator_mode;
	int m_column_width;
	int m_progressbar_height;
	int m_progressbar_border_width;
	int m_nonplayable_margins;
	int m_items_distances;

	std::string m_progress_unit;
	int m_numbering_mode;
};

#endif
