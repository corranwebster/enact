"""
Multi Iris Plot Example
=======================

In this example we display three scatter plots of the iris data, one for each
species.
"""
import numpy

from traits.api import HasTraits, Instance, List, Str, Array, Enum, File, \
    Tuple, Int, Button, Any, Property, cached_property, on_trait_change
from traitsui.api import View, Group, VGroup, HGroup, Item, spring, CheckListEditor, InstanceEditor, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from pyface.api import MessageDialog, FileDialog
from enact.api import get_transition_manager, PlotDataTransition
from enable.api import ComponentEditor
from chaco.api import ArrayPlotData, Plot, ScatterInspectorOverlay, marker_trait, jet
from chaco.tools.api import PanTool, ZoomTool, DragZoom

from iris import load_iris, iris_dtype

# this is the code from the iris_tabular example, modified to track the selection

class IrisAdapter(TabularAdapter):
    """ This is an adapter that maps the iris dtype to the TabularEditor columns
    and also knows how to get the value of the cell.
    """
    columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'species']
    
    def get_text(self, object, trait, row, column):
        return str(getattr(object, trait)[row][column])

class IrisDataset(HasTraits):
    """ A dataset loaded from a file, displayed in a Tabular editor.
    """
    filename = File
    
    open_file = Button
    
    update = Button
    
    data = Property(Array(dtype=iris_dtype), depends_on='filename')
    
    selection = List(Int)
    
    def _open_file_changed(self):
        dlg = FileDialog()
        if dlg.open():
            self.filename = dlg.path
    
    @cached_property
    def _get_data(self):
        """ The filename has changed, so try to read in a new dataset.
        
        Note that we can display the array directly.
        """
        if not self.filename:
            return numpy.array([], dtype=iris_dtype)
        try:
            # load into an array
            return load_iris(self.filename)
        except Exception, exc:
            dlg = MessageDialog(title='Could not open file %s' % self.filename,
                message=str(exc))
            dlg.open()
            return numpy.array([], dtype=iris_dtype)
    
    traits_view = View(
        VGroup(
            HGroup(
                Item('open_file'),
                Item('filename', style='readonly', springy=True),
                Item('update'),
                show_labels=False,
            ),
            Item('data', style='custom',
                editor=TabularEditor(
                    adapter=IrisAdapter(),
                    multi_select=True,
                    selected_row='selection',
                ),
            ),
            show_labels=False,
        ),
        height=600,
        width=400,
        resizable=True,
    )

# plotting code

class IrisPlot(HasTraits):

    # the IrisDataset holding the actual array
    dataset = Instance(IrisDataset)
    
    # a local reference to the data array in the dataset, for convenience
    data = Property(Array(dtype=iris_dtype), depends_on='dataset.data')
    
    # numerical dtype components
    numerical_items = Property(List(Str), depends_on='data')
    
    # categorical dtype components
    categorical_items = Property(List(Tuple(Str, List)), depends_on='data')

    # traits for selecting axes and colours 
    x_axis = Enum(values='numerical_items')
    y_axis = Enum(values='numerical_items')
    color = Enum(values='numerical_items')

    # the list of species, used to populate plots
    species = List(Str, ['setosa', 'versicolor', 'virginica'])
    
    # a corresponding list of markers to use for each species
    markers = List(marker_trait, ['square', 'circle', 'triangle'])
    
    # the list of species with visible plot renderers
    visible_plots = List(Str, ['setosa', 'versicolor', 'virginica'])

    # ArrayPlotData for plot
    plot_data = Instance(ArrayPlotData, ())
    
    # Chaco Plot instance
    plot = Instance(Plot)
    
    transition_manager = Any
    
    def _transition_manager_default(self):
        transition_manager = get_transition_manager()
        transition_manager.heartbeat
        return transition_manager

    @cached_property
    def _get_data(self):
        return self.dataset.data
    
    @cached_property
    def _get_numerical_items(self):
        d = self.data.dtype
        return [name for name in d.names if d[name].kind in 'iufc']
    
    @cached_property
    def _get_catgeorical_items(self):
        
        d = self.data.dtype
        result = []
        for name in d.names:
            values = numpy.unique(self.data[name])
            if len(values) <= 10:
                result.append((name, values))
        return values
        
    @on_trait_change('x_axis,y_axis,color,data,plot,dataset.update')
    def _data_source_change(self):
        """Handler for changes to the data source selectors
        """
        for species in self.species:
            # get masks for each species
            mask = self.data['species'] == ('Iris-'+species)
            # set default arrays
            transition_index = PlotDataTransition(
                ease = 'array_ease_in',
                plot_data = self.plot_data,
                data_key = species+'_index',
                duration = 1.0,
                final = self.data[self.x_axis][mask],
            )
            transition_value = PlotDataTransition(
                ease = 'array_ease_in',
                plot_data = self.plot_data,
                data_key = species+'_value',
                duration = 1.0,
                final = self.data[self.y_axis][mask],
            )
            transition_color = PlotDataTransition(
                ease = 'array_ease_in',
                plot_data = self.plot_data,
                data_key = species+'_color',
                duration = 1.0,
                final = self.data[self.color][mask],
            )
            self.transition_manager.connect(transition_index)
            self.transition_manager.connect(transition_value)
            self.transition_manager.connect(transition_color)
            #self.plot_data.set_data(species+'_index', self.data[self.x_axis][mask])
            #self.plot_data.set_data(species+'_value', self.data[self.y_axis][mask])
            #self.plot_data.set_data(species+'_color', self.data[self.color][mask])
        
        # set axis titles appropriately
        self.plot.x_axis.title=self.x_axis.title()
        self.plot.y_axis.title=self.y_axis.title()
    
    @on_trait_change('dataset.selection')
    def user_selection_changed(self, new):
        """ We extract the selection from the dataset, and filter by 
        species.
        """
        # ensure the plot exists
        self.plot
        
        # turn the selection list of indices into a mask
        selection = numpy.zeros(shape=len(self.data), dtype=bool)
        selection[new] = True
        
        for i, species in enumerate(self.species):
            # get mask for each species
            mask = self.data['species'] == ('Iris-'+species)
            # mask the mask to get the selection for each species
            species_selection = selection[mask]
            # now get the indices
            indx = list(numpy.arange(len(self.data))[species_selection])
            # set the metadata on the renderer
            self.renderers[i].index.metadata['selections'] = indx
    
    def _visible_plots_changed(self, new):
        """User has changed the list of visible plots
        """
        for i, species in enumerate(self.species):
            self.renderers[i].visible = (species in new)
        self.plot.request_redraw()
    
    def _plot_data_default(self):
        """ This creates a list of ArrayPlotData instances,
        one for each species.
        """
        plot_data = ArrayPlotData()
        for species in self.species:
            # set empty default arrays
            plot_data.set_data(species+'_index', [])
            plot_data.set_data(species+'_value', [])
            plot_data.set_data(species+'_color', [])
        return plot_data
    
    def _plot_default(self):
        """ This creates the default value for the plot.
        """
        # create the main plot object
        plot = Plot(self.plot_data)
        
        # create a renderer for each species, with a different marker for each
        self.renderers = []
        for species, marker in zip(self.species, self.markers):
            renderer = plot.plot(
                (species+'_index', species+'_value', species+'_color'),
                type="cmap_scatter",
                color_mapper=jet,
                marker=marker
            )[0]

            self.renderers.append(renderer)

            # inspector tool for showing data about points
            #renderer.tools.append(ScatterInspector(renderer))
            
            # overlay for highlighting selected points
            overlay = ScatterInspectorOverlay(renderer,
                hover_color="red",
                hover_marker_size=6,
                selection_marker_size=6,
                selection_color="yellow",
                selection_outline_color="black",
                selection_line_width=3)
            renderer.overlays.append(overlay)
        
        # add the additional information
        plot.title = 'Iris Data'
        plot.x_axis.title=''
        plot.y_axis.title=''        

        # tools for basic interactivity
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        plot.tools.append(DragZoom(plot, drag_button="right"))

        return plot
        
    traits_view = View(
        HGroup(
            Item('dataset', show_label=False, style='custom',
                editor=InstanceEditor()),
            VGroup(
                HGroup(
                    Group(
                        Item('x_axis'),
                        Item('y_axis'),
                        Item('color'),
                    ),
                    Item('visible_plots', show_label=False, style='custom',
                        editor=CheckListEditor(name='species')
                    ),
                    spring,
                ),
                Item('plot', show_label=False, editor=ComponentEditor()),
            ),
        ),
        width=900, height=600,
        resizable=True,
        title='Iris Plot',
    )

if __name__ == '__main__':
    dataset = IrisDataset(filename='iris.csv')
    iris_plot = IrisPlot(dataset=dataset)
    iris_plot.configure_traits()
